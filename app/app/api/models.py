from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Reason class
class Reason(models.Model):

    class ProfileDataType(models.TextChoices):
        AGE = 'A', _('Age')
        GENDER = 'G', _('Gender')
        LOCATION = 'L', _('Location')
        PERSONALITY = 'P', _('Personality')

    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    profile_data_type = models.CharField(
        max_length=1, 
        choices=ProfileDataType.choices
    )
    reason = models.TextField(max_length=1000, blank=True, null=True)

# Profile data class
class ProfileData(models.Model):

    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        UNKNOWN = 'U', _('Unknown')

    age = models.TextField(max_length=50, blank=True, null=True)
    gender = models.CharField(
        max_length=1, 
        choices=Gender.choices,
        default=Gender.UNKNOWN
    )
    location = models.TextField(max_length=100, blank=True, null=True)
    personality = models.TextField(max_length=100, blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return '%s, %s, %s, %s' % (self.age, self.gender, self.location, self.personality)

# Comment class
class Comment(models.Model):
    date = models.DateTimeField()
    text = models.TextField(max_length=1000)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)

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
    is_valid = models.BooleanField()
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