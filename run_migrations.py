import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nids_project.settings')
django.setup()

try:
    print("Executing database schema upgrade...")
    call_command('makemigrations', 'detection')
    call_command('migrate', 'detection')
    print("SUCCESS: Database schema is now synchronized with the ATHEX suite.")
except Exception as e:
    print(f"FAILURE: Migration failed with error: {e}")
