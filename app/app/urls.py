"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from app.api import views
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve as serve_static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'export', views.ExportViewSet, 'export')
router.register(r'globaldata', views.GlobalDataViewSet, 'globaldata')
router.register(r'corpus', views.CorpusViewSet, 'corpus')
router.register(r'comments', views.CommentViewSet, 'comments')
router.register(r'labeleddata', views.LabeledDataViewSet, 'labeleddata')

handler404 = 'app.web.views.handler404'

def _static_butler(request, path, **kwargs):
    return serve_static(request, path, insecure=True, **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login', views.login),
    path('', include('app.web.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^celery-progress/', include('celery_progress.urls')),
    re_path(r'static/(.+)', _static_butler),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico')))
]
