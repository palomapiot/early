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

TOKEN = "Token "
AUTHORIZATION = "Authorization"
GLOBALDATA_ENDPOINT = '/api/globaldata/1/'

def _api_request(request, url, request_type='GET', body=None):
    protocol = 'http://'
    if request.is_secure():
        protocol = 'https://'
    token, _ = Token.objects.get_or_create(user=request.user)
    if request_type == 'GET':
        response = requests.get(protocol + request.get_host() + url,
        headers={AUTHORIZATION:TOKEN + token.key})
    if request_type == 'PUT':
        response = requests.put(protocol + request.get_host() + url,
        headers={AUTHORIZATION:TOKEN + token.key}, json=body)
    if request_type == 'POST':
        response = requests.post(protocol + request.get_host() + url,
        headers={AUTHORIZATION:TOKEN + token.key}, json=body)
    return response.json()

def profiles(request):
    try:
        active_page = int(request.GET['page'])
    except:
        active_page = 1
    try:
        path_vars = '&experiment_id=' + request.GET.get('experiment_id', '')
        # Age filter
        if request.GET.get('age', '') != '':
            for age_val in request.GET.getlist('age', ''):
                path_vars += '&validated_data__age=' + age_val
        # Gender filter
        if request.GET.get('gender', '') != '':
            for gender_val in request.GET.getlist('gender', ''):
                path_vars += '&validated_data__gender=' + gender_val
        # Location filter
        if request.GET.get('location', '') != '':
            for location_val in request.GET.getlist('location', ''):
                path_vars += '&validated_data__location=' + location_val
        # Gender filter
        if request.GET.get('personality', '') != '':
            for personality_val in request.GET.getlist('personality', ''):
                path_vars += '&validated_data__personality=' + personality_val
        # Depression filter
        if request.GET.get('depressed', '') != '':
            for depressed_val in request.GET.getlist('depressed', ''):
                path_vars += '&validated_data__depressed=' + depressed_val
        # Processed filter
        if request.GET.get('processed', '') != '':
            for processed_val in request.GET.getlist('processed', ''):
                path_vars += '&processed=' + processed_val
        # Valid profile filter
        if request.GET.get('is_valid', '') != '':
            for is_valid_val in request.GET.getlist('is_valid', ''):
                path_vars += '&is_valid=' + is_valid_val

        json_request = _api_request(request, '/api/profiles/?page=' 
            + str(active_page) 
            + path_vars
        )
        total_pages = math.ceil(json_request['count'] / REST_FRAMEWORK['PAGE_SIZE'])
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
        globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
        return render(request, 'profiles.html', {
            'results': json_request['results'],
            'previous': None if json_request['previous'] is None else active_page - 1,
            'next': None if json_request['next'] is None else active_page + 1,
            'pages': pages,
            'globaldata': globaldata
        })
    except:
        raise Http404

def profile_detail(request, pk):
    json_request = _api_request(request, '/api/profiles/' + str(pk))
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    corpus = _api_request(request, '/api/corpus/', 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json_request,
        'globaldata': globaldata, 
        'all_corpus': corpus['results']
    })

def edit_profile(request, pk):
    body = {
        "corpus": int(request.POST.get("corpus")),
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
    json_request = _api_request(request, '/api/profiles/' + str(pk) + '/', 'PUT', body)
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json_request,
        'globaldata': globaldata
    })

def index(request):
    globaldata = {}
    if request.user.is_authenticated:
        globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
        if request.user.groups.filter(name="eadmin").exists():
            corpus = _api_request(request, '/api/corpus/', 'GET')
            return render(request, 'administration.html', {'globaldata': globaldata, 'all_corpus': corpus['results']})
        return profiles(request)
    return render(request, 'index.html', {'globaldata': globaldata})

def export(request):
    opts = request.POST.get("exportOptions")
    if opts == 'demographic':
        export_format = request.POST.get("demographicFormat")
        response = export_demographic(request, export_format)
    else:
        corpus = request.POST.get("corpus")
        export_format = request.POST.get("datasetFormat")
        response = export_dataset(request, export_format, corpus)
    return response

def export_demographic(request, export_format):
    json_request = _api_request(request, '/api/export/')
    if export_format == 'JSON':
        response = JsonResponse(json_request, content_type='application/json', safe=False)
        response['Content-Disposition'] = 'attachment; filename="export.json"'
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Experiment ID', 'Age', 'Gender', 'Location', 'Personality', 'Depressed'])
        for obj in json_request:
            data = obj['validated_data']
            writer.writerow([obj['experiment_id'], data['age'], data['gender'], data['location'], data['personality'], data['depressed']])
    return response

def export_dataset(request, export_format, corpus):
    print('TODO: next sprint')
    print(export_format)
    print(corpus)
    return redirect('/')

def loaddata(request):
    subreddit = request.POST.get("subreddit")
    nsubmissions = request.POST.get("nsubmissions")
    nusers = request.POST.get("nusers")
    ncomments = request.POST.get("ncomments")
    corpus = request.POST.get("corpus")
    load_reddit_data.delay(request.user.id, request.is_secure(), 'web:8000', subreddit, nsubmissions, nusers, ncomments, corpus)
    return redirect('/')


def createcorpus(request):
    body = {
        "corpus_name": request.POST.get("corpus_name")
    }
    _api_request(request, '/api/corpus/', 'POST', body)
    return redirect('/')

def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, 'Password successfully changed.')
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    return render(request, 'account.html', {'globaldata': globaldata})

