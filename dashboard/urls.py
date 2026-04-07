# URL Configuration for Dashboard - Force Reload
from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='landing.html', redirect_authenticated_user=False), name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('alerts/', views.alerts, name='alerts'),
    path('logs/', views.logs, name='logs'),
    path('settings/', views.settings, name='settings'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('settings/blacklist/add/', views.add_blacklist, name='add_blacklist'),
    path('settings/blacklist/remove/', views.remove_blacklist, name='remove_blacklist'),
    path('settings/profile/update/', views.update_profile, name='update_profile'),
    path('clear-data/', views.clear_data, name='clear_data'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    path('api/classification-data/', views.api_classification_data, name='api_classification_data'),
    path('export-telemetry/', views.export_logs_csv, name='master_export_csv'),
    path('api/alerts/', views.api_recent_alerts, name='api_recent_alerts'),
    path('api/recent-logs/', views.api_recent_logs, name='api_recent_logs'),
    path('debesh/', views.debesh, name='dashboard_debesh'),
]
