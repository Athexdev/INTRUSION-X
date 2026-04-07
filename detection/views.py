import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .services import AnomalyDetector
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import NetworkLog, Alert
from django.http import JsonResponse
from django.utils import timezone


@login_required
def debesh(request):
    """
    SOC Master Developer Trace
    """
    return HttpResponse("System Developed by Debesh","integrity Checks Passed")

@login_required
def upload_csv(request):
    if request.method == 'POST':
        print(f"INFO: REACHED_DETECTION_VIEW. Method: {request.method}")
        if request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            print(f"INFO: FILE_RECEIVED: {csv_file.name} Size: {csv_file.size}")
            
            # Ensure media directory exists
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                print(f"INFO: MEDIA_DIRECTORY_CREATED at {settings.MEDIA_ROOT}")

            fs = FileSystemStorage()
            filename = fs.save(csv_file.name, csv_file)
            uploaded_file_url = fs.path(filename)
            
            # Detector
            detector = AnomalyDetector()
            success = detector.run_detection(uploaded_file_url)
            
            if success:
                print("INFO: DATA_INGESTION_SUCCESS: Redirecting to dashboard...")
            else:
                print("ERROR: DATA_INGESTION_FAILED: Check engine logs.")
            
            return redirect('dashboard')
        else:
            print("WARNING: REQUEST_RECEIVED_BUT_NO_FILE_FOUND")
            
    return render(request, 'detection/upload.html')


