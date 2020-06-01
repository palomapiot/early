import csv
import requests
from app.web.reddit import get_submissions, get_users, get_user_comments
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from django.http import Http404, HttpResponse
from django.contrib import messages
from app.settings import REST_FRAMEWORK
import math as math
import asyncio

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped

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
    if requestType == 'POST':
        response = requests.post(protocol + request.get_host() + url,
        headers={"Authorization":"Token " + token.key}, json=body)
    #print(response.json())
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
        if request.user.groups.filter(name = "eadmin").exists():
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

def loaddata(request):
    print('initttttttttttttttttt')
    #submissions = get_submissions("depression")
    #users = get_users(submissions)
    #print(users)
    users = ['maninashed', 'Spirituuus', 'rbllmelba', 'return_idol', 'D8nkmemelord']  
    #download_thread = threading.Thread(target=_process_all_users, args=(request, users))
    #download_thread.start()
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    for user in users:
        print('forrrrrrrrrrrrrrrr: ')
        print(user)
        _process_user(request, user)

    print('loaddddddddddddddddddddddddddddddddd')
    return render(request, 'account.html', {})

def password_change_done(request):
    messages.add_message(request, messages.SUCCESS, 'Password successfully changed.')
    return render(request, 'account.html', {})

def _process_all_users(request, users):
    for user in users:
        _process_user(request, user)

#@background
def _process_user(request, user):
    print('processsssssssssssssssssssss: ')
    print(user)
    comments = get_user_comments(user)
    body = {
        "experiment_id": str(user),
        "reddit_username": str(user),
        "comments": comments
    }
    print('lets call request')
    _api_request(request, '/api/profiles/', 'POST', body)
