from django.shortcuts import render, redirect # RELOAD_MARKER
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from detection.models import NetworkLog, Alert, BlacklistedIP, SystemSetting
from django.http import JsonResponse, HttpResponse
import csv
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta



@login_required
def debesh(request):
    """
    SOC Master Developer Trace
    """
    return HttpResponse("System Developed by Debesh")


@login_required
def dashboard_view(request):
    context = {
        'packets_analyzed': NetworkLog.objects.count(),
        'anomalies_detected': NetworkLog.objects.filter(prediction=-1).count(),
        'active_connections': NetworkLog.objects.values('src_ip').distinct().count(),
        'threat_level': 'High' if NetworkLog.objects.filter(prediction=-1).count() > 10 else 'Low',
        'recent_logs': NetworkLog.objects.all().order_by('-timestamp')[:10],
        'recent_alerts': Alert.objects.all().order_by('-timestamp')[:5],
        'alert_count': Alert.objects.count() # DYNAMIC_BADGE
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def api_stats(request):
    # Detailed stats for auto-refresh
    packets_analyzed = NetworkLog.objects.count()
    active_connections = NetworkLog.objects.values('src_ip').distinct().count()
    anomalies_detected = NetworkLog.objects.filter(prediction=-1).count()
    anomaly_ratio = (anomalies_detected / packets_analyzed * 100) if packets_analyzed > 0 else 0
    threat_level = 'LOW' if anomaly_ratio < 2 else ('MEDIUM' if anomaly_ratio < 7 else 'HIGH')
    
    data = {
        'packets': packets_analyzed,
        'active': active_connections,
        'anomalies': anomalies_detected,
        'threat_level': threat_level
    }
    return JsonResponse(data)

@login_required
def api_chart_data(request):
    # Fetch data for the last 30 minutes
    now = timezone.now()
    labels = []
    normal_data = []
    anomaly_data = []

    for i in range(29, -1, -1):
        time_slot = now - timedelta(minutes=i)
        start_time = time_slot.replace(second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=1)
        
        labels.append(start_time.strftime('%H:%M'))
        
        count_normal = NetworkLog.objects.filter(
            timestamp__gte=start_time,
            timestamp__lt=end_time,
            prediction=1
        ).count()
        
        count_anomaly = NetworkLog.objects.filter(
            timestamp__gte=start_time,
            timestamp__lt=end_time,
            prediction=-1
        ).count()
        
        normal_data.append(count_normal)
        anomaly_data.append(count_anomaly)

    return JsonResponse({
        'labels': labels,
        'normal_data': normal_data,
        'anomaly_data': anomaly_data
    })

@login_required
def api_classification_data(request):
    # Donut chart: Safe, Warning, Critical
    safe_count = NetworkLog.objects.filter(prediction=1).count()
    critical_count = NetworkLog.objects.filter(prediction=-1).count()
    warning_count = Alert.objects.filter(severity='Medium').count()
    
    return JsonResponse({
        'safe': safe_count,
        'warning': warning_count,
        'critical': critical_count
    })

@login_required
def alerts(request):
    recent_alerts = Alert.objects.all().order_by('-timestamp')
    alert_count = Alert.objects.count()
    return render(request, 'dashboard/alerts.html', {
        'recent_alerts': recent_alerts,
        'alert_count': alert_count
    })

@login_required
def logs(request):
    logs = NetworkLog.objects.all().order_by('-timestamp')
    alert_count = Alert.objects.count()
    return render(request, 'dashboard/logs.html', {
        'logs': logs,
        'alert_count': alert_count
    })

@login_required
def settings(request):
    alert_count = Alert.objects.count()
    blacklisted_ips = BlacklistedIP.objects.all().order_by('-timestamp')
    
    # Get nodes with hit counts
    active_nodes = NetworkLog.objects.values('src_ip').annotate(hit_count=Count('id')).order_by('-hit_count')[:10]
    
    try:
        nids_contamination = SystemSetting.objects.get(key='nids_contamination').value
    except:
        nids_contamination = '0.1'

    return render(request, 'dashboard/settings.html', {
        'alert_count': alert_count,
        'blacklisted_ips': blacklisted_ips,
        'active_nodes': active_nodes,
        'nids_contamination': nids_contamination
    })

@login_required
def update_settings(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        value = request.POST.get('value')
        SystemSetting.objects.update_or_create(key=key, defaults={'value': value})
    return redirect('settings')

@login_required
def add_blacklist(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        if ip:
            BlacklistedIP.objects.get_or_create(ip_address=ip, reason="Admin Manual Block")
    return redirect('settings')

@login_required
def remove_blacklist(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        BlacklistedIP.objects.filter(ip_address=ip).delete()
    return redirect('settings')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # 1. Update Username
        if new_username and new_username != user.username:
            user.username = new_username
            user.save()
            print(f"INFO: [SEC_OPS] IDENTITY_UPDATED_TO: {new_username}")

        # 2. Update Password
        if new_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user) # Don't log out
                print("INFO: [SEC_OPS] AUTH_TOKEN_ROTATED")
                messages.success(request, 'Credential patch successful.')
            else:
                messages.error(request, 'Auth Token mismatch.')
                print("WARNING: [SEC_OPS] AUTH_PATCH_REJECTED: Mismatch")
        
    return redirect('settings')

@login_required
def export_logs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nids_network_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Packet Size', 'Duration', 'Anomaly Score', 'Status'])

    logs = NetworkLog.objects.all().order_by('-timestamp')
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.src_ip,
            log.dst_ip,
            log.protocol,
            log.packet_size,
            log.duration,
            log.anomaly_score,
            log.status
        ])
    return response



@login_required
def api_recent_alerts(request):
    alerts = Alert.objects.order_by('-timestamp')[:5]
    data = [{
        'type': a.type,
        'message': a.message,
        'severity': a.severity,
        'timestamp': a.timestamp.strftime('%H:%M:%S')
    } for a in alerts]
    return JsonResponse({'alerts': data})

@login_required
def api_recent_logs(request):
    logs = NetworkLog.objects.order_by('-timestamp')[:10]
    data = [{
        'src_ip': l.src_ip,
        'dst_ip': l.dst_ip,
        'protocol': l.protocol,
        'packet_size': l.packet_size,
        'anomaly_score': round(l.anomaly_score, 4),
        'status': l.status
    } for l in logs]
    return JsonResponse({'logs': data})

@login_required
def clear_data(request):
    if request.method == 'POST':
        NetworkLog.objects.all().delete()
        Alert.objects.all().delete()
        return redirect('dashboard')
    return redirect('settings')


