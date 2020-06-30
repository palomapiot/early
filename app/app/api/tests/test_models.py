from django.test import TestCase
from app.api.models import Reason, Profile, ProfileData
from django_countries.fields import CountryField

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
        profile_data = ProfileData.objects.create(age="20-30", gender="Female", location='AU', personality="Agreeableness", depressed=False)

    def test_profile_data(self):
        data = ProfileData.objects.get(id=1)
        self.assertEquals(isinstance(data.age, str), True)
        self.assertEquals(isinstance(data.gender, str), True)
        self.assertEquals(data.location.name, "Australia")
        self.assertEquals(isinstance(data.personality, str), True)
        self.assertEquals(isinstance(data.depressed, bool), True)
