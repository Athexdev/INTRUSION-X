import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from .models import NetworkLog, Alert, BlacklistedIP, SystemSetting
from django.utils import timezone
from datetime import timedelta
import random

class AnomalyDetector:
    def __init__(self):
        # Default sensitivity
        self.contamination = 0.1
        self.lof = LocalOutlierFactor(n_neighbors=20, contamination=self.contamination)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

    def preprocess_data(self, df):
        # Ensure correct columns
        expected_cols = ['src_ip', 'dst_ip', 'packet_size', 'protocol', 'duration']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0 if col in ['packet_size', 'duration'] else '0.0.0.0'
                if col == 'protocol': df[col] = 'TCP'
        
        # Encode Protocol (Must exist now)
        df['protocol_encoded'] = self.label_encoder.fit_transform(df['protocol'].astype(str))
        
        # Features for LOF
        features = ['packet_size', 'protocol_encoded', 'duration']
        X = df[features].values
        
        # Scaling
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled

    def run_detection(self, csv_file_path):
        print(f"INFO: [NIDS_CORE] ANALYZING_TELEMETRY: {csv_file_path}")
        try:
            # 1. Fetch Dynamic Settings
            try:
                setting = SystemSetting.objects.get(key='nids_contamination')
                self.contamination = float(setting.value)
            except:
                self.contamination = 0.1 # Default fallback

            # 2. Fetch Blacklisted IPs
            blacklisted_ips = list(BlacklistedIP.objects.values_list('ip_address', flat=True))

            df = pd.read_csv(csv_file_path)
            if df.empty:
                print("WARNING: [NIDS_CORE] TELEMETRY_STREAM_EMPTY")
                return []

            X_scaled = self.preprocess_data(df)
            
            # 3. Dynamic neighbor and contamination scaling
            n_samples = len(X_scaled)
            k_neighbors = min(20, n_samples - 1 if n_samples > 1 else 1)
            
            # Re-init LOF with admin-tuned contamination
            self.lof = LocalOutlierFactor(n_neighbors=k_neighbors, contamination=self.contamination)
            
            # LOF prediction (1 for inliers, -1 for outliers)
            predictions = self.lof.fit_predict(X_scaled)
            negative_outlier_factor = self.lof.negative_outlier_factor_
            
            ingested_count = 0
            anomalies = []
            now = timezone.now()
            
            print(f"INFO: [NIDS_CORE] CLASSIFYING {len(df)} PACKETS...")

            for i, row in df.iterrows():
                try:
                    src_ip = row.get('src_ip', '0.0.0.0')
                    
                    # 4. Check Blacklist
                    is_blacklisted = src_ip in blacklisted_ips
                    
                    if is_blacklisted:
                        pred = -1
                        score = 5.0 # Max severity
                        status = 'Critical'
                    else:
                        pred = int(predictions[i])
                        score = float(negative_outlier_factor[i])
                        status = 'Safe' if pred == 1 else 'Critical'

                    # Centralized distribution (centered around 15 mins ago)
                    offset_minutes = random.randint(8, 22)
                    offset_seconds = random.randint(0, 59)
                    log_time = now - timedelta(minutes=offset_minutes, seconds=offset_seconds)
                    
                    if pred == -1:
                        anomalies.append(row)
                    
                    # Create and Save explicitly
                    log = NetworkLog(
                        src_ip=src_ip,
                        dst_ip=row.get('dst_ip', '0.0.0.0'),
                        packet_size=int(row.get('packet_size', 0)),
                        protocol=row.get('protocol', 'TCP').upper()[:10],
                        duration=float(row.get('duration', 0.0)),
                        prediction=pred,
                        anomaly_score=score,
                        status=status,
                        timestamp=log_time
                    )
                    log.save()
                    ingested_count += 1
                except Exception as row_error:
                    print(f"ERROR: [NIDS_CORE] PACKET_RECORD_FAILURE at row {i}: {row_error}")

            print(f"SUCCESS: [NIDS_CORE] {ingested_count} PACKETS COMMITTED TO SECURE ARCHIVE.")
            
            # Engine to generate alerts
            self.generate_alerts(anomalies)
            
            return True

        except Exception as e:
            print(f"CRITICAL: [NIDS_CORE] ANALYZER_FAILURE: {e}")
            return False

    def generate_alerts(self, anomalies):
        if not anomalies:
            return
        
        src_ips = [a.get('src_ip') for a in anomalies]
        from collections import Counter
        ip_counts = Counter(src_ips)
        
        for ip, count in ip_counts.items():
            if count >= 3:
                Alert.objects.create(
                    type='Port Scan',
                    message=f"Possible port scan detected from source IP: {ip}. Count: {count} anomalous hits.",
                    severity='High'
                )
            else:
                Alert.objects.create(
                    type='Unknown Anomaly',
                    message=f"Single suspicious packet pattern detected from source IP: {ip}.",
                    severity='Medium'
                )
        
        if len(anomalies) > 5:
            Alert.objects.create(
                type='Traffic Spike',
                message=f"Detected burst of {len(anomalies)} anomalies in recent telemetry injection.",
                severity='High'
            )
