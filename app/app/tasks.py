import os

import requests
from celery import Celery, current_task
from django.conf import settings
from celery_progress.backend import ProgressRecorder
from app.web.reddit import get_user_comments
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

def _api_request(request_user, request_is_secure, request_host, url, request_type='GET', body=None):
    from rest_framework.authtoken.models import Token
    protocol = 'http://'
    if request_is_secure:
        protocol = 'https://'
    token, _ = Token.objects.get_or_create(user=request_user)
    if request_type == 'POST':
        response = requests.post(protocol + request_host + url, headers={"Authorization":"Token " + token.key}, json=body)
    if request_type == 'PUT':
        response = requests.put(protocol + request_host + url, headers={"Authorization":"Token " + token.key}, json=body)
    return response.json()

@app.task
def process_user(request_user, request_is_secure, request_host, user):
    comments = get_user_comments(user)
    body = {
        "experiment_id": str(user),
        "reddit_username": str(user),
        "comments": comments
    }
    _api_request(request_user, request_is_secure, request_host, '/api/profiles/', 'POST', body)

@app.task(bind=True, name="load_data")
def load_reddit_data(self, request_user, request_is_secure, request_host):
    from app.web.reddit import get_submissions, get_users
    print('puto asco de vida')
    body = {
        "load_in_progress": True,
        "task_id": str(current_task.request.id)
    }
    _api_request(request_user, request_is_secure, request_host, '/api/globaldata/1/', 'PUT', body)
    #submissions = get_submissions("depression")
    #users = get_users(submissions)
    users = ['bastardlass', 'kjirstinn', 'cmarq07', 'Kocheeze', 'TheBlackMambas87']
    print('los usuarios')
    total_work_to_do = len(users)
    progress_recorder = ProgressRecorder(self)
    result = 0
    progress_recorder.set_progress(result, total_work_to_do)
    for user in users:
        print('cada usuarios')
        time.sleep(30)
        process_user.delay(request_user, request_is_secure, request_host, user)
        result += 1
        # tell the progress observer how many out of the total items we have processed
        progress_recorder.set_progress(result, total_work_to_do)
    
    end_body = {
        "load_in_progress": False,
        "task_id": None
    }
    _api_request(request_user, request_is_secure, request_host, '/api/globaldata/1/', 'PUT', end_body)
