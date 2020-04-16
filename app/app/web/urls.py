from django.urls import path, include
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
import app

urlpatterns = [
    path('account/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('account/', TemplateView.as_view(template_name='account.html'), name='account'),
    path('profiles/', views.profiles, name='profiles'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile-detail'),
    path('export/', views.export, name='export'),
    path('administration/', TemplateView.as_view(template_name='administration.html'), name='administration'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]