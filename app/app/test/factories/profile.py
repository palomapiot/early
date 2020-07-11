import factory
from app.api.models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        #django_get_or_create = ('experiment_id')
        # Defaults (can be overrided)
    experiment_id = 'behave_test_1'
    id = 1
