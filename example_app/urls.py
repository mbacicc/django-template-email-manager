from django.urls import path, re_path
from django.conf.urls import url, include
from . import views
from django.views.generic import TemplateView

app_name = 'example_app'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('examples/', views.ExamplesView.as_view(), name='examples'),
    path('examples/1', views.Example1View, name='example1'),
    path('examples/2', views.Example2View, name='example2'),
    re_path(r'^download-fixture/(?P<fixture_id>\d+)/$', views.DownloadFixtureView, name='download_fixture'),

    
]
