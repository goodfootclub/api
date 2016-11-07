from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models


# Overview
#
# 1. User sings up
# 2. Users joins a team (finds by the name)
# 3. Team joins an event
#
#
# Captain (user) creates a team
#   With team name
#   Can add users to the team
# Captain creates an event
#
#
#   / - home screen (my schedule)
#   /events - all events
#   /events/:id - specific event
#
# For new events
#  location
#  time&date
#  two teams


class Team(models.Model):
    """Team"""
    manager = models.ForeignKey(User, related_name='managed_teams')
    name = models.CharField(max_length=255)
    players = models.ManyToManyField(User, related_name='teams')

    def __unicode__(self):
        return "Team(name='{name}')".format(name=self.name)


class TeamRole(models.Model):
    """Role of a player in a Team (captain, field, substitute, etc...)
    """
    CAPTAIN = 'CAP'
    FIELD = 'FLD'
    SUBSTITUTE = 'SUB'

    ROLE_CHOICES = (
        (CAPTAIN, CAPTAIN),
        (FIELD, FIELD),
        (SUBSTITUTE, SUBSTITUTE),
    )

    player = models.ForeignKey(User)
    role = models.CharField(max_length=3, choices=ROLE_CHOICES,
                            default=FIELD)
    team = models.ForeignKey(Team)


class Location(models.Model):
    """
    Game location
    """
    address = models.CharField(max_length=255)
    gis = gis_models.PointField(null=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "Location(name='{name}')".format(name=self.name)


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
    location = models.ForeignKey(Location, related_name='games')
    organizer = models.ForeignKey(User, related_name='games_created')
    teams = models.ManyToManyField(Team, related_name='games')


class RsvpStatus(models.Model):
    """
    Whether or not a player attends a game
    """

    GOING = 'G'
    NOT_GOING = 'N'
    UNDEFINED = 'U'

    RSVP_CHOICES = (
        (GOING, GOING),
        (NOT_GOING, NOT_GOING),
        (UNDEFINED, UNDEFINED),
    )

    game = models.ForeignKey(Game, related_name='rsvps')
    player = models.ForeignKey(User, related_name='rsvps')
    status = models.CharField(max_length=255, choices=RSVP_CHOICES,
                              default=UNDEFINED)
