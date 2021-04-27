from django.urls import path, re_path
from django.conf.urls import url, include
from . import views
from django.views.generic import TemplateView

app_name = 'example_app'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('example1/', views.Example1View, name='example1'),
    re_path(r'^download-fixture/(?P<fixture_id>\d+)/$', views.DownloadFixtureView, name='download_fixture'),

    
]
