import requests
from django.contrib import auth
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from django.http import HttpResponseRedirect

# Create your views here.

def profiles(request):
    protocol = 'http://'
    if request.is_secure():
        protocol = 'https://'
    token, _ = Token.objects.get_or_create(user=request.user)
    response = requests.get(protocol + request.get_host() + '/api/profiles/', headers={"Authorization":"Token " + token.key})
    json = response.json()
    return render(request, 'profiles.html', {
        'results': json['results']
    })

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, 'administration.html', {})
        return profiles(request)
    return render(request, 'index.html', {})
