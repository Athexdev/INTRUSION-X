import os
import sys
import django
from django.core.management import execute_from_command_line

def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nids_project.settings')
    django.setup()

    print("--- Activating ATHEX v4.2.0 Project Helper Script ---")
    
    # 1. Migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    # 2. Create Superuser if not exists
    from django.contrib.auth.models import User
    if not User.objects.filter(username='DEBESH N1').exists():
        print("Creating superuser (DEBESH N1 / athexdev09)...")
        User.objects.create_superuser('DEBESH N1', 'athexdev@gmail.com', 'athexdev09')
    else:
        print("Superuser already exists.")

    print("\n--- Setup Complete! ---")
    print("Run 'python manage.py runserver' to start the SOC Dashboard.")

if __name__ == "__main__":
    run()
