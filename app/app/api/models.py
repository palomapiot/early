from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

# Reason class
class Reason(models.Model):

    class ProfileDataType(models.TextChoices):
        AGE = 'Age', _('Age')
        GENDER = 'Gender', _('Gender')
        LOCATION = 'Location', _('Location')
        PERSONALITY = 'Personality', _('Personality')
        DEPRESSION = 'Depression', _('Depression')

    profile = models.ForeignKey('Profile', related_name='reasons', on_delete=models.CASCADE)
    profile_data_type = models.TextField(
        choices=ProfileDataType.choices
    )
    reason = models.TextField(max_length=1000, blank=True, null=True)

# Profile data class
class ProfileData(models.Model):

    class Age(models.TextChoices):
        ADOLESCENCE = '12-20', _('12-20')
        EARLY_ADULTHOOD = '20-30', _('20-30')
        MATURE_ADULTHOOD = '30-65', _('30-65')
        OLD_AGE = 'Over65', _('Over65')
        UNKNOWN = 'Unknown', _('Unknown')

    class Gender(models.TextChoices):
        MALE = 'Male', _('Male')
        FEMALE = 'Female', _('Female')
        UNKNOWN = 'Unknown', _('Unknown')

    class Personality(models.TextChoices):
        EXTRAVERSION = 'Extraversion', _('Extraversion')
        AGREEABLENESS = 'Agreeableness', _('Agreeableness')
        CONSCIENTIOUSNESS = 'Conscientiousness', _('Conscientiousness')
        NEUROTICISM = 'Neuroticism', _('Neuroticism')
        OPENNESS = 'Openness', _('Openness')
        UNKNOWN = 'Unknown', _('Unknown')

    age = models.TextField(
        choices=Age.choices,
        default=Age.UNKNOWN
    )
    gender = models.TextField(
        choices=Gender.choices,
        default=Gender.UNKNOWN
    )
    location = CountryField(blank_label='', blank=True, null=True)
    personality = models.TextField(
        choices=Personality.choices,
        default=Personality.UNKNOWN
    )
    depressed = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        """String for representing the Model object."""
        return '%s, %s, %s, %s' % (self.age, self.gender, self.location, self.personality)

# Comment class
class Comment(models.Model):
    date = models.DateTimeField()
    text = models.TextField()
    profile = models.ForeignKey('Profile', related_name='comments', on_delete=models.CASCADE)

# Profile class
class Profile(models.Model):
    experiment_id = models.TextField(max_length=50)
    reddit_username = models.TextField(max_length=50, blank=True, null=True)
    system_data = models.ForeignKey(
        ProfileData, 
        on_delete=models.CASCADE,
        related_name='%(class)s_system_data',
        blank=True,
        null=True
    )
    is_valid = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    validated_data = models.ForeignKey(
        ProfileData, 
        on_delete=models.CASCADE,
        related_name='%(class)s_validated_data',
        blank=True,
        null=True
    )
    processed = models.BooleanField(default=False)
    last_retrieved_comment_date = models.DateTimeField(blank=True, null=True)

class GlobalData(models.Model):
    load_in_progress = models.BooleanField(default=False)
    task_id = models.TextField(max_length=100, blank=True, null=True)