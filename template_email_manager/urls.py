from django.urls import path
from . import views

app_name = 'template_email_manager'
urlpatterns = [
    path('process-emails/', views.process_emails, name='process_emails'),
    path('add-test-email/', views.add_test_email, name='add_test_email'),
]
