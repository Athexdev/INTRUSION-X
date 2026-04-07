from django.db import models
from django.utils import timezone

class NetworkLog(models.Model):
    PROTOCOL_CHOICES = [
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('ICMP', 'ICMP'),
    ]
    
    src_ip = models.GenericIPAddressField()
    dst_ip = models.GenericIPAddressField()
    packet_size = models.IntegerField()
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES)
    duration = models.FloatField(default=0.0)
    prediction = models.IntegerField() # 1: Normal, -1: Anomaly
    anomaly_score = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='Safe') # Safe / Warning / Critical
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.src_ip} -> {self.dst_ip} ({self.status})"

class Alert(models.Model):
    ALERT_TYPES = [
        ('Port Scan', 'Port Scan'),
        ('Traffic Spike', 'Traffic Spike'),
        ('Brute Force', 'Brute Force'),
        ('Unknown Anomaly', 'Unknown Anomaly'),
    ]
    
    type = models.CharField(max_length=50, choices=ALERT_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=10, default='Medium') # Low, Medium, High

    def __str__(self):
        return f"{self.type} - {self.severity}"

class BlacklistedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address

class SystemSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
