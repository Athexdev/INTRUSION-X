import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nids_project.settings')
django.setup()

from detection.models import NetworkLog, Alert

def check_status():
    print("--- SOC SYSTEM PULSE DIAGNOSTIC ---")
    
    packet_count = NetworkLog.objects.count()
    anomaly_count = NetworkLog.objects.filter(prediction=-1).count()
    alert_count = Alert.objects.count()
    
    print(f"Total Packets in DB: {packet_count}")
    print(f"Anomalies Detected:  {anomaly_count}")
    print(f"Total Alerts:        {alert_count}")
    
    if packet_count > 0:
        latest = NetworkLog.objects.latest('timestamp')
        oldest = NetworkLog.objects.order_by('timestamp').first()
        print(f"Data Time Range:     {oldest.timestamp.strftime('%H:%M:%S')} to {latest.timestamp.strftime('%H:%M:%S')}")
        print(f"Current System Time: {timezone.now().strftime('%H:%M:%S')}")
        
    print("\n--- RECENT ACTIVITY CHECK ---")
    recent = NetworkLog.objects.all().order_by('-id')[:5]
    for log in recent:
        print(f"LOG: {log.src_ip} -> {log.dst_ip} | Status: {log.status} | Time: {log.timestamp.strftime('%H:%M:%S')}")

    if packet_count == 0:
        print("\nWARNING: Database is currently EMPTY. Telemetry ingestion is failing.")
    else:
        print("\nSUCCESS: Database contains data. Visualization mismatch suspected.")

if __name__ == "__main__":
    check_status()
