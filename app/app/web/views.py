import csv
import requests
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.core import serializers
from django.shortcuts import redirect
from app.settings import REST_FRAMEWORK
import math as math
from app.tasks import load_reddit_data
from celery.result import AsyncResult
import json
import time

# Create your views here.

def _api_request(request, url, request_type='GET', body=None):
    protocol = 'http://'
    if request.is_secure():
        protocol = 'https://'
    token, _ = Token.objects.get_or_create(user=request.user)
    if request_type == 'GET':
        response = requests.get(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key})
    if request_type == 'PUT':
        response = requests.put(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key}, json=body)
    if request_type == 'POST':
        response = requests.post(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key}, json=body)
    return response.json()

def profiles(request):
    try:
        active_page = int(request.GET['page'])
    except:
        active_page = 1
    try:
        json = _api_request(request, '/api/profiles/?page=' + str(active_page))
        total_pages = math.ceil(json['count'] / REST_FRAMEWORK['PAGE_SIZE'])
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
        globaldata = _api_request(request, '/api/globaldata/1/', 'GET')
        return render(request, 'profiles.html', {
            'results': json['results'],
            'previous': None if json['previous'] == None else active_page - 1,
            'next': None if json['next'] == None else active_page + 1,
            'pages': pages,
            'globaldata': globaldata
        })
    except:
        raise Http404 

def profile_detail(request, pk):
    json = _api_request(request, '/api/profiles/' + str(pk))
    globaldata = _api_request(request, '/api/globaldata/1/', 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json,
        'globaldata': globaldata
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
    globaldata = _api_request(request, '/api/globaldata/1/', 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json,
        'globaldata': globaldata
    })

def index(request):
    globaldata = {}
    if request.user.is_authenticated:
        globaldata = _api_request(request, '/api/globaldata/1/', 'GET')
        print(globaldata)
        if request.user.groups.filter(name = "eadmin").exists():
            return render(request, 'administration.html', {'globaldata': globaldata})
        return profiles(request)
    return render(request, 'index.html', {'globaldata': globaldata})

def export(request):
    opts = request.POST.get("exportOptions")
    if opts == 'demographic':
        export_format = request.POST.get("demographicFormat")
        response = export_demographic(request, export_format)
    else:
        export_format = request.POST.get("datasetFormat")
        response = export_dataset(request, export_format)
    return response

def export_demographic(request, export_format):
    json_data = _api_request(request, '/api/export/')
    if export_format == 'JSON':
        response = JsonResponse(json_data, content_type='application/json', safe=False)
        response['Content-Disposition'] = 'attachment; filename="export.json"'
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Experiment ID', 'Age', 'Gender', 'Location', 'Personality', 'Depressed'])
        for obj in json_data:
            data = obj['validated_data']
            writer.writerow([obj['experiment_id'], data['age'], data['gender'], data['location'], data['personality'], data['depressed']])
    return response

def export_dataset(request, export_format):
    print('TODO: next sprint')
    return 'OK'

def loaddata(request):
    result = load_reddit_data.delay(request.user.id, request.is_secure(), request.get_host())
    print('the result is:')
    print(result)
    return redirect('/')

def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, 'Password successfully changed.')
    globaldata = _api_request(request, '/api/globaldata/1/', 'GET')
    return render(request, 'account.html', {'globaldata': globaldata})

