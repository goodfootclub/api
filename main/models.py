from django.db import models
from django.contrib.gis.db import models as gis_models

from users.models import User


class Team(models.Model):
    """Team"""
    manager = models.ForeignKey(User, related_name='old_managed_teams')
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(User, related_name='old_teams')

    def __unicode__(self):
        return "Team(name='{name}')".format(name=self.name)

    def __str__(self):
        return "{name}".format(name=self.name)


class Location(models.Model):
    """
    Game location
    """
    address = models.CharField(max_length=255)
    gis = gis_models.PointField(null=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "Location(name='{name}')".format(name=self.name)

    def __str__(self):
        return "{name}".format(name=self.name)


class Game(models.Model):
    """
    Game event

    Fields
        id
        datetime: DateTime;
        duration?: number - minutes
        description?: string
        location: Location
        teams?: number - two team
        organizer?: user - creator of an event
    """

    datetime = models.DateTimeField()
    description = models.CharField(null=True, blank=True, max_length=255)
    duration = models.IntegerField(null=True)
    location = models.ForeignKey(Location, related_name='old_games')
    organizer = models.ForeignKey(User, related_name='old_games_created')
    teams = models.ManyToManyField(Team, related_name='old_games')


class RsvpStatus(models.Model):
    """
    Whether or not a player attends a game
    """

    GOING = 'G'
    NOT_GOING = 'N'
    UNCERTAIN = 'U'

    RSVP_CHOICES = (
        (GOING, GOING),
        (NOT_GOING, NOT_GOING),
        (UNCERTAIN, UNCERTAIN),
    )

    game = models.ForeignKey(Game, related_name='old_rsvps')
    player = models.ForeignKey(User, related_name='old_rsvps')
    status = models.CharField(max_length=1, choices=RSVP_CHOICES,
                              default=UNCERTAIN)
