import os
import pickle

import requests
from celery import Celery, current_task
from django.conf import settings
from celery_progress.backend import ProgressRecorder
from app.web.reddit import get_user_comments
from classifiers.gender import preprocess
import json
import time

import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, KFold, RepeatedKFold
from sklearn.utils.class_weight import compute_class_weight
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# load gender model
GENDER_MODEL = pickle.load(open(os.path.join('classifiers', 'gender'), 'rb'))

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

    # TODO: before creating -> classify calling the gender model and save the system data
    text = ':::'.join([comment['text'] for comment in comments])

    # preprocess comments
    df = preprocess(str(user), text)

    df = df.drop(columns=['third_person_pron_count', 'square_brackets_count', 'CONJ', 'EOL', 'NO_TAG']) 

    # predict
    gender = GENDER_MODEL.predict(df.drop(['text', 'author_id'], axis=1))

    gender_output = 'Unknown'
    if gender[0] == 'male':
        gender_output = 'Male'
    elif gender[0] == 'female':
        gender_output = 'Female'

    body = {
        "experiment_id": str(user),
        "reddit_username": str(user),
        "comments": comments,
        "system_data":
        {
            "age": "Unknown",
            "gender": gender_output,
            "location": None,
            "personality": "Unknown",
            "depressed": None
        }
    }
    # create / update profile
    _api_request(request_user, request_is_secure, request_host, '/api/profiles/', 'POST', body)

@app.task(bind=True, name="load_data")
def load_reddit_data(self, request_user, request_is_secure, request_host):
    from app.web.reddit import get_submissions, get_users
    body = {
        "load_in_progress": True,
        "task_id": str(current_task.request.id)
    }
    _api_request(request_user, request_is_secure, request_host, '/api/globaldata/1/', 'PUT', body)
    # TODO: switch in order to have the complete funtionality
    #submissions = get_submissions("depression")
    #users = get_users(submissions)
    users = ['SQLwitch', 'joshhelp155', 'tangerinetofu', 'SmellaShitsgerald']
    total_work_to_do = len(users)
    progress_recorder = ProgressRecorder(self)
    result = 0
    progress_recorder.set_progress(result, total_work_to_do)
    for user in users:
        time.sleep(3)
        process_user.delay(request_user, request_is_secure, request_host, user)
        result += 1
        # tell the progress observer how many out of the total items we have processed
        progress_recorder.set_progress(result, total_work_to_do)
    
    end_body = {
        "load_in_progress": False,
        "task_id": None
    }
    _api_request(request_user, request_is_secure, request_host, '/api/globaldata/1/', 'PUT', end_body)
