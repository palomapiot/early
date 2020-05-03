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
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from app.settings import REST_FRAMEWORK
import json
import math as m

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
    try:
        active_page = int(request.GET['page'][0])
    except:
        active_page = 1
    try:
        json = _api_request(request, '/api/profiles/?page=' + str(active_page))
        total_pages = m.ceil(json['count'] / REST_FRAMEWORK['PAGE_SIZE'])
        pages = []
        if total_pages <= 7:
            for page in range(1, total_pages + 1):
                pages.append({'page': page, 'active': page == active_page})
        else:
            if active_page <= 4:
                for page in range(1, 6):
                    pages.append({'page': page, 'active': page == active_page})
                pages.append({'page': '...', 'active': False})
                pages.append({'page': total_pages, 'active': False})
            elif active_page >= total_pages - 3:
                pages.append({'page': 1, 'active': False})
                pages.append({'page': '...', 'active': False})
                for page in range(total_pages - 4, total_pages + 1):
                    pages.append({'page': page, 'active': page == active_page})
            else:
                pages.append({'page': 1, 'active': False})
                pages.append({'page': '...', 'active': False})
                pages.append({'page': active_page - 1, 'active': False})
                pages.append({'page': active_page, 'active': True})
                pages.append({'page': active_page + 1, 'active': False})
                pages.append({'page': '...', 'active': False})
                pages.append({'page': total_pages, 'active': False})
        return render(request, 'profiles.html', {
            'results': json['results'],
            'previous': None if json['previous'] == None else active_page - 1,
            'next': None if json['next'] == None else active_page + 1,
            'pages': pages,
        })
    except:
        raise Http404 

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
            "depressed": request.POST.get("depressed") if request.POST.get("depressed") is not None else False
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
    #messages.add_message(request, messages.SUCCESS, 'Export successfully completed.')
    return response

def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, 'Password successfully changed.')
    return render(request, 'account.html', {})