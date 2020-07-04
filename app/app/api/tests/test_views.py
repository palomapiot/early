import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase, force_authenticate
from app.api.models import Reason, Profile, ProfileData, Comment, GlobalData

BODY = {
        "experiment_id": "test_case1",
        "reddit_username": "",
        "system_data": {
            "age": "20-30",
            "gender": "Female",
            "location": "Austria",
            "personality": "Agreeableness",
            "depressed": True
        },
        "reasons": [
            {
                "profile_data_type": "Age",
                "reason": "user said she was 25"
            },
            {
                "profile_data_type": "Gender",
                "reason": "user said she was a woman"
            }
        ],
        "comments": [
            {
                "date": "2019-06-05T23:43",
                "text": "I am 20 years old"
            },
            {
                "date": "2019-06-03T18:36",
                "text": "i got my period..."
            }
        ]
    }

class ProfilesTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_profiles(self):
        response = self.client.get('/api/profiles/', format='json')
        self.assertEqual(response.status_code, 200)

class ExportTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_export(self):
        response = self.client.get('/api/export/', format='json')
        self.assertEqual(response.status_code, 200)

class ProfilePostTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_post_profiles(self):
        response = self.client.post('/api/profiles/', BODY, format='json')
        self.assertEqual(response.status_code, 201)

class ProfileTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        profile = self.client.post('/api/profiles/', BODY, format='json')
        data = json.loads(str(profile.content, encoding='utf8'))
        response = self.client.get('/api/profiles/' + str(data['id']) + '/', format='json')
        self.assertEqual(response.status_code, 200)

class ProfileEditTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_put_profile(self):
        profile = self.client.post('/api/profiles/', BODY, format='json')
        data = json.loads(str(profile.content, encoding='utf8'))
        edition = {
            "validated_data": {
                "age": "20-30",
                "gender": "Female",
                "location": "Sweden",
                "personality": "Agreeableness",
                "depressed": True
            },
            "validated_by": {"username": "me"}
        }
        response = self.client.put('/api/profiles/' + str(data['id']) + '/', edition, format='json')
        updated_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_data['is_valid'], True)

class ReasonTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_reasons(self):
        profile = self.client.post('/api/profiles/', BODY, format='json')
        data = json.loads(str(profile.content, encoding='utf8'))
        response = self.client.get('/api/profiles/' + str(data['id']) + '/reasons/?type=Age', format='json')
        reasons = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reasons, ['user said she was 25'])

class GlobalDataTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_globaldata(self):
        response = self.client.get('/api/globaldata/', format='json')
        self.assertEqual(response.status_code, 200)

class GlobalDataCreateTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_post_globaldata(self):
        globaldata = {
            "load_in_progress": True,
            "task_id": "6ca7c616-d2d8-442a-9af7-074d8f4aef9c"
        }

        response = self.client.post('/api/globaldata/', globaldata, format='json')
        self.assertEqual(response.status_code, 201)