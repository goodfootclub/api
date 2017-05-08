from datetime import timedelta
from random import randint

from django.contrib.gis.geos import Point
from django.utils import timezone
from mixer.backend.django import mixer


__all__ = ['mixer']

mixer.register(
    'games.Location',
    gis=lambda: Point(
        float(mixer.faker.latitude()),
        float(mixer.faker.longitude()),
    ),
)

# For testing we need to create games in the future by default
mixer.register(
    'games.Game',
    datetime=timezone.now() + timedelta(randint(1, 500)),
)
