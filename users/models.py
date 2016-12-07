from django.contrib.auth.models import AbstractUser
from django.db import models

from timezone_field import TimeZoneField


class User(AbstractUser):
    """
    Default django user plus some custom fields
    """
    FEMALE = 'F'
    MALE = 'M'

    GENDER_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    bio = models.TextField()
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    img = models.ImageField()
    phone = models.CharField(max_length=12)
    profile_complete = models.BooleanField(default=False)
    timezone = TimeZoneField()

    class Meta(AbstractUser.Meta):
        pass
