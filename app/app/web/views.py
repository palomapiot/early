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
from app.tasks import load_reddit_data, process_user
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

def _export_demographic(request, export_format):
    json_request = _api_request(request, '/api/export/')
    if export_format == 'JSON':
        new_request = []
        for element in json_request:
            new_request.append(flatten_json(element))
        response = JsonResponse(new_request, content_type='application/json', safe=False)
        response['Content-Disposition'] = 'attachment; filename="demographics-export.json"'
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="demographics-export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'experiment_id', 'age', 'gender', 'location', 'personality', 'depressed'])
        for obj in json_request:
            data = obj['validated_data']
            writer.writerow([obj['id'], obj['experiment_id'], data['age'], data['gender'], data['location'], data['personality'], data['depressed']])
    return response

def _export_dataset(request, export_format, corpus):
    if corpus == "":
        json_request = _api_request(request, '/api/comments')
    else:
        json_request = _api_request(request, '/api/comments?corpus=' + corpus)
    if export_format == 'JSON':
        response = JsonResponse(json_request, content_type='application/json', safe=False)
        response['Content-Disposition'] = 'attachment; filename="corpus-export.json"'
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="corpus-export.csv"'

        writer = csv.writer(response)
        writer.writerow(['id', 'corpus', 'comments'])
        for obj in json_request:
            comments = obj['comments']
            for comment in comments:
                writer.writerow([obj['id'], obj['corpus'], comment['date'], comment['text']])
    return response

def _export_labeled_data(request, export_format, corpus, labels, drop):
    if corpus == "":
        json_request = _api_request(request, '/api/labeleddata')
    else:
        json_request = _api_request(request, '/api/labeleddata?corpus=' + corpus)
    if export_format == 'JSON':
        new_request = []
        for element in json_request:
            out = flatten_json(element)
            for key in drop:
                del out[key] 
            new_request.append(out)
        response = JsonResponse(new_request, content_type='application/json', safe=False)
        response['Content-Disposition'] = 'attachment; filename="labeled-data-export.json"'
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="labeled-data-export.csv"'

        writer = csv.writer(response)
        columns = ['id', 'corpus', 'date', 'text'] + labels
        writer.writerow(columns)
        for obj in json_request:
            data = obj['validated_data']
            comments = obj['comments']
            for comment in comments:
                data_list = [data[key] for key in labels]
                row = [obj['id'], obj['corpus'], comment['date'], comment['text']] + data_list
                writer.writerow(row)
    return response

def _calculate_depression_level(questionnaire):
    depression_level = "unknown"
    if questionnaire != None:
        # depression level score
        depression_levels = {
            "minimal depression": range(0, 9),
            "mild depression": range(10, 18),
            "moderate depression": range(19, 29),
            "severe depression": range(30, 63)
        }
        level_score = sum(int(i[0]) for i in questionnaire.values())
        for key, value in depression_levels.items():
            if level_score in value:
                depression_level = key
                break
    return depression_level

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
    depression_level = _calculate_depression_level(json_request["questionnaire"])
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    corpus = _api_request(request, '/api/corpus/', 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json_request,
        'depression_level': depression_level,
        'globaldata': globaldata, 
        'all_corpus': corpus['results']
    })

def questionnaire(request, pk):
    body = {
        "questionnaire":
        {
            "q1": request.POST.get("q1") if request.POST.get("q1") is not None else '0',
            "q2": request.POST.get("q2") if request.POST.get("q2") is not None else '0',
            "q3": request.POST.get("q3") if request.POST.get("q3") is not None else '0',
            "q4": request.POST.get("q4") if request.POST.get("q4") is not None else '0',
            "q5": request.POST.get("q5") if request.POST.get("q5") is not None else '0',
            "q6": request.POST.get("q6") if request.POST.get("q6") is not None else '0',
            "q7": request.POST.get("q7") if request.POST.get("q7") is not None else '0',
            "q8": request.POST.get("q8") if request.POST.get("q8") is not None else '0',
            "q9": request.POST.get("q9") if request.POST.get("q9") is not None else '0',
            "q10": request.POST.get("q10") if request.POST.get("q10") is not None else '0',
            "q11": request.POST.get("q11") if request.POST.get("q11") is not None else '0',
            "q12": request.POST.get("q12") if request.POST.get("q12") is not None else '0',
            "q13": request.POST.get("q13") if request.POST.get("q13") is not None else '0',
            "q14": request.POST.get("q14") if request.POST.get("q14") is not None else '0',
            "q15": request.POST.get("q15") if request.POST.get("q15") is not None else '0',
            "q16": request.POST.get("q16") if request.POST.get("q16") is not None else '0',
            "q17": request.POST.get("q17") if request.POST.get("q17") is not None else '0',
            "q18": request.POST.get("q18") if request.POST.get("q18") is not None else '0',
            "q19": request.POST.get("q19") if request.POST.get("q19") is not None else '0',
            "q20": request.POST.get("q20") if request.POST.get("q20") is not None else '0',
            "q21": request.POST.get("q21") if request.POST.get("q21") is not None else '0'
        },
        "validated_by": {"username": "me"}
    }
    json_request = _api_request(request, '/api/profiles/' + str(pk) + '/', 'PUT', body)
    depression_level = _calculate_depression_level(json_request["questionnaire"])
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json_request,
        'depression_level': depression_level,
        'globaldata': globaldata
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
        "validated_by": {"username": "mes"}
    }
    json_request = _api_request(request, '/api/profiles/' + str(pk) + '/', 'PUT', body)
    depression_level = _calculate_depression_level(json_request["questionnaire"])
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    return render(request, 'profile_detail.html', {
        'profile': json_request,
        'depression_level': depression_level,
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
        response = _export_demographic(request, export_format)
    elif opts == 'dataset':
        corpus = request.POST.get("corpus")
        export_format = request.POST.get("datasetFormat")
        response = _export_dataset(request, export_format, corpus)
    else:
        corpus = request.POST.get("corpus")
        export_format = request.POST.get("labeledDataFormat")
        labels_obj = {
            'age': request.POST.get("age") != None,
            'gender': request.POST.get("gender") != None,
            'location': request.POST.get("location") != None,
            'personality': request.POST.get("personality") != None,
            'depressed': request.POST.get("depression") != None,
        }
        labels_dict = { k: v for k, v in labels_obj.items() if v }
        labels = [key for key in labels_dict.keys()]
        drop_dict = { k: v for k, v in labels_obj.items() if v == False}
        drop = [key for key in drop_dict.keys()]
        response = _export_labeled_data(request, export_format, corpus, labels, drop)
    return response

def loaddata(request):
    subreddit = request.POST.get("subreddit")
    nsubmissions = request.POST.get("nsubmissions")
    nusers = request.POST.get("nusers")
    ncomments = request.POST.get("ncomments")
    corpus = request.POST.get("corpus")
    host = 'web:8000'
    load_reddit_data.delay(request.user.id, request.is_secure(), host, subreddit, nsubmissions, nusers, ncomments, corpus)
    return redirect('/')


def createcorpus(request):
    body = {
        "corpus_name": request.POST.get("corpus_name")
    }
    _api_request(request, '/api/corpus/', 'POST', body)
    return redirect('/')

def processuser(request):
    username = request.POST.get("username")
    ncomments = request.POST.get("ncomments")
    corpus = request.POST.get("corpus")
    host =  'web:8000' # request.get_host() 
    process_user.delay(request.user.id, request.is_secure(), host, username, ncomments, corpus)
    return redirect('/')

def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, 'Password successfully changed.')
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    return render(request, 'account.html', {'globaldata': globaldata})

def update_user(request):
    globaldata = _api_request(request, GLOBALDATA_ENDPOINT, 'GET')
    if request.method == "POST":
        body = {
            "username": str(request.user.username),
            "email": request.POST.get("email"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name")
        }
        _api_request(request, '/api/users/' + str(request.user.id) + '/', 'PUT', body)
        return render(request, 'account.html', {'globaldata': globaldata})
    else:
        data = _api_request(request, '/api/users/' + str(request.user.id), 'GET')
        return render(request, 'update_user.html', {'globaldata': globaldata, 'form': data})

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a)
        else:
            out[name] = x

    flatten(y)
    return out

def handler404(request, *args, **argv):
    response = render(request,'404.html', {})
    response.status_code = 404
    return response
