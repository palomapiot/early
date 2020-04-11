from django.urls import path, include
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
import app

urlpatterns = [
    path('account/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('account/', TemplateView.as_view(template_name='account.html'), name='account'),
]