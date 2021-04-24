from django.urls import path, re_path
from django.conf.urls import url, include
from . import views
from django.views.generic import TemplateView

app_name = 'example_app'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add_email/', views.AddEmailView, name='add_email'),

    
]
