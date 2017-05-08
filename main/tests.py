import pytz
from django.contrib.gis.geos import Point
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
    datetime=mixer.faker.date_time_between(start_date='now', tzinfo=pytz.UTC),
)
