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

PROFILES_ENDPOINT = '/api/profiles/'
GLOBALDATA_ENDPOINT = '/api/globaldata/'
EXPORT_ENDPOINT = '/api/export/'


class ProfilesTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_profiles(self):
        response = self.client.get(PROFILES_ENDPOINT, format='json')
        self.assertEqual(response.status_code, 200)


class ExportTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_export(self):
        response = self.client.get(EXPORT_ENDPOINT, format='json')
        self.assertEqual(response.status_code, 200)


class ProfilePostTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_post_profiles(self):
        response = self.client.post(PROFILES_ENDPOINT, BODY, format='json')
        self.assertEqual(response.status_code, 201)


class ProfileTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        profile = self.client.post(PROFILES_ENDPOINT, BODY, format='json')
        data = json.loads(str(profile.content, encoding='utf8'))
        response = self.client.get(
            PROFILES_ENDPOINT + str(data['id']) + '/', format='json')
        self.assertEqual(response.status_code, 200)


class ProfileEditTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_put_profile(self):
        profile = self.client.post(PROFILES_ENDPOINT, BODY, format='json')
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
        response = self.client.put(
            PROFILES_ENDPOINT + str(data['id']) + '/', edition, format='json')
        updated_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_data['is_valid'], True)


class ReasonTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_reasons(self):
        profile = self.client.post(PROFILES_ENDPOINT, BODY, format='json')
        data = json.loads(str(profile.content, encoding='utf8'))
        response = self.client.get(
            PROFILES_ENDPOINT + str(data['id']) + '/reasons/?type=Age', format='json')
        reasons = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reasons, ['user said she was 25'])


class GlobalDataTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_get_globaldata(self):
        response = self.client.get(GLOBALDATA_ENDPOINT, format='json')
        self.assertEqual(response.status_code, 200)


class GlobalDataCreateTestCase(APITestCase):
    def setUp(self):
        self.username = 'john_doe'
        self.password = 'foobar'
        self.user = User.objects.create(
            username=self.username, password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_post_globaldata(self):
        globaldata = {
            "load_in_progress": True,
            "task_id": "6ca7c616-d2d8-442a-9af7-074d8f4aef9c"
        }

        response = self.client.post(
            GLOBALDATA_ENDPOINT, globaldata, format='json')
        self.assertEqual(response.status_code, 201)
