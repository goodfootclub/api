from datetime import timedelta
from random import randint

import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone
from mixer.backend.django import mixer
from rest_framework.test import APIClient


__all__ = ['mixer']

mixer.register(
    'games.Location',
    gis=lambda: Point(
        float(mixer.faker.latitude()),
        float(mixer.faker.longitude()),
    ),
)

# Create games in the future by default
mixer.register(
    'games.Game',
    datetime=timezone.now() + timedelta(randint(1, 500)),
)


@pytest.fixture
def client():
    """Authenticated client fixture"""
    client = APIClient()
    client.user = mixer.blend('users.User')
    client.force_authenticate(user=client.user)
    return client
