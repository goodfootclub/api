
from django.contrib.gis.db import models

from teams.models import Team
from users.models import User


class Location(models.Model):
    """Game location

    Fields:
        address (String) - address
        gis? (Point) - lat lng coordinates
        name (String) - display name
    """
    address = models.CharField(max_length=255, blank=True, null=True)
    gis = models.PointField(null=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "Location(name='{name}')".format(name=self.name)

    def __str__(self):
        return "{name}".format(name=self.name)


class Game(models.Model):
    """Game event

    Fields:
        datetime (DateTime) - Time and date for an event;
        duration? (Int) - number in minutes
        description? (String) - notes, reminders, etc...
        location (FK) - Location, place where a game will take place
        teams? (MtM) - 0, 1 or 2 teams (pickup games have no teams)
        organizer? (FK) - User, creator of an event
    """

    datetime = models.DateTimeField()
    description = models.CharField(null=True, blank=True, max_length=255)
    duration = models.IntegerField(null=True)
    location = models.ForeignKey(Location, related_name='games')
    organizer = models.ForeignKey(User, related_name='games_created')
    teams = models.ManyToManyField(Team, related_name='games')
    players = models.ManyToManyField(User, related_name='games',
                                     through='RsvpStatus')

    class Meta:
        ordering = ['-datetime']


class RsvpStatus(models.Model):
    """Player <-> Game relationship. Whether or not a player attends a game,
    invited to, or asks to join a game.

    Fields:
        game (FK) - a game event
        player (FK) - a player that...
        status (Int) - ... is one of the following:
            - invited to the game
            - requested to join the game
            - will attend the game
            - won't attend the game
            - not sure
        team (Int) - team number (0 or 1). 2 for when teams are decided on
            the spot or player doesn't care which side to take
    """
    GOING = 2
    UNCERTAIN = 1
    NOT_GOING = 0
    INVITED = -1
    REQUESTED_TO_JOIN = -2

    RSVP_CHOICES = (
        (GOING, 'Going'),
        (INVITED, 'Invited'),
        (NOT_GOING, 'Not going'),
        (REQUESTED_TO_JOIN, 'Asked to join'),
        (UNCERTAIN, 'Not sure'),
    )

    NO_TEAM = 2

    game = models.ForeignKey(Game, related_name='rsvps')
    player = models.ForeignKey(User, related_name='rsvps')
    status = models.IntegerField(choices=RSVP_CHOICES, default=INVITED)
    team = models.IntegerField(default=NO_TEAM)

    class Meta:
        unique_together = 'player', 'game'
        ordering = ['-status']
        verbose_name = 'RSVP status'
        verbose_name_plural = 'RSVP statuses'
