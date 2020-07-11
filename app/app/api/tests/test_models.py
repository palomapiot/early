from django.test import TestCase
from app.api.models import Reason, Profile, ProfileData, Comment, GlobalData
from django_countries.fields import CountryField
import datetime


class ReasonModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        profile = Profile.objects.create(experiment_id="test_subject")
        profile.reasons.create(profile_data_type="Age", reason="Reason")

    def test_reason(self):
        reason = Reason.objects.get(id=1)
        max_length = reason._meta.get_field('reason').max_length
        self.assertEquals(max_length, 1000)
        self.assertEquals(isinstance(reason.profile_data_type, str), True)
        self.assertEquals(isinstance(reason.reason, str), True)
        self.assertEquals(isinstance(reason.profile, Profile), True)


class ProfileDataModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        ProfileData.objects.create(
            age="20-30", gender="Female", location='AU', personality="Agreeableness", depressed=False)

    def test_profile_data(self):
        data = ProfileData.objects.get(id=1)
        self.assertEquals(isinstance(data.age, str), True)
        self.assertEquals(isinstance(data.gender, str), True)
        self.assertEquals(data.location.name, "Australia")
        self.assertEquals(isinstance(data.personality, str), True)
        self.assertEquals(isinstance(data.depressed, bool), True)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        profile = Profile.objects.create(experiment_id="test_subject")
        profile.comments.create(
            date="2020-02-16T07:26:22+00:00", text="I am a female")

    def test_comment(self):
        data = Comment.objects.get(id=1)
        self.assertEquals(isinstance(data.date, datetime.datetime), True)
        self.assertEquals(isinstance(data.text, str), True)


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Profile.objects.create(experiment_id="test_subject")

    def test_profile(self):
        data = Profile.objects.first()
        self.assertEquals(isinstance(data.experiment_id, str), True)


class GlobalDataModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        GlobalData.objects.create(
            load_in_progress=True, task_id="d52cd57a-86ba-4ccf-bc24-6bd2743ca627")

    def test_globaldata(self):
        data = GlobalData.objects.get(id=1)
        self.assertEquals(isinstance(data.load_in_progress, bool), True)
        self.assertEquals(isinstance(data.task_id, str), True)
