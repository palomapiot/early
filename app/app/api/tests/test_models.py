from django.test import TestCase
from app.api.models import Reason, Profile, ProfileData

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
        profile_data = ProfileData.objects.create(age="20", gender="Female", location="Austria", personality="Extrovert", depressed=False)

    def test_reason_max_length(self):
        data = ProfileData.objects.get(id=1)
        age_max_length = data._meta.get_field('age').max_length
        self.assertEquals(age_max_length, 50)
        self.assertEquals(isinstance(data.gender, str), True)
        self.assertEquals(isinstance(data.location, str), True)
        self.assertEquals(isinstance(data.personality, str), True)
        self.assertEquals(isinstance(data.depressed, bool), True)
