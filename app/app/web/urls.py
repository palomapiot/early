"""
    Copyright 2020-2021 Paloma Piot Pérez-Abadín
	
	This file is part of early.
    early is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    early is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with early.  If not, see <https://www.gnu.org/licenses/>.
"""

from django.urls import path, include
from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
import app

urlpatterns = [
    path('account/password_change/done/', views.password_change_done), 
    path('account/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('account/', TemplateView.as_view(template_name='account.html'), name='account'),
    path('account/update_user/', views.update_user, name='update_user'),
    path('profiles/', views.profiles, name='profiles'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile-detail'),
    path('profiles/<int:pk>/edit/', views.edit_profile, name='edit-profile'),
    path('profiles/<int:pk>/questionnaire/', views.questionnaire, name='questionnaire'),
    path('export/', views.export, name='export'),
    path('loaddata/', views.loaddata, name='loaddata'),
    path('createcorpus/', views.createcorpus, name='createcorpus'),
    path('processuser/', views.processuser, name='processuser'),
    path('administration/', TemplateView.as_view(template_name='administration.html'), name='administration'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]