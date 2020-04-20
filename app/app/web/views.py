import csv
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
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
import json

# Create your views here.

def _api_request(request, url, requestType='GET', body=None):
    protocol = 'http://'
    if request.is_secure():
        protocol = 'https://'
    token, _ = Token.objects.get_or_create(user=request.user)
    if requestType == 'GET':
        response = requests.get(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key})
    if requestType == 'PUT':
        response = requests.put(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key}, json=body)
    return response.json()

def profiles(request):
    json = _api_request(request, '/api/profiles/')
    return render(request, 'profiles.html', {
        'results': json['results']
    })

def profile_detail(request, pk):
    json = _api_request(request, '/api/profiles/' + str(pk))
    return render(request, 'profile_detail.html', {
        'profile': json
    })

def edit_profile(request, pk):
    body = {
        "validated_data":
        {
            "age": request.POST.get("age"),
            "gender": request.POST.get("gender"),
            "location": request.POST.get("location"),
            "personality": request.POST.get("personality"),
            "depressed": request.POST.get("depressed")
        },
        "validated_by": {"username": "me"}
    }
    json = _api_request(request, '/api/profiles/' + str(pk) + '/', 'PUT', body)
    return render(request, 'profile_detail.html', {
        'profile': json
    })

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, 'administration.html', {})
        return profiles(request)
    return render(request, 'index.html', {})

def export(request):
    json = _api_request(request, '/api/export/')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Experiment ID', 'Age', 'Gender', 'Location', 'Personality', 'Depressed'])
    for obj in json['results']:
        data = obj['validated_data']
        writer.writerow([obj['experiment_id'], data['age'], data['gender'], data['location'], data['personality'], data['depressed']])
    #messages.add_message(request, messages.INFO, 'Export successfully completed.')
    return response
