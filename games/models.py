from datetime import datetime, timedelta

from django.contrib.gis.db import models

from teams.models import Team


class Location(models.Model):
    """
    Game location

    Fields:
        address? (String) - address
        gis? (Point) - STRID 4326 gis coordinates
        name (String) - display name
    """
    address = models.CharField(max_length=255, blank=True, null=True)
    gis = models.PointField(null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'Location(name={self.name!r}, address={self.address!r})'

    class Meta:
        unique_together = ('address', 'name')


class Game(models.Model):
    """
    Game event

    Fields:
        datetime (DateTime) - Time and date for an event;
        description? (String) - notes, reminders, etc...
        duration? (Int) - number in minutes
        location (FK) - Location, place where a game will take place
        organizer? (FK) - User, creator of an event
        teams? (MtM) - 0, 1 or 2 teams (pickup games have no teams)
    """

    datetime = models.DateTimeField()
    description = models.CharField(blank=True, max_length=255, default='')
    duration = models.IntegerField(null=True)
    location = models.ForeignKey(Location, related_name='games')
    organizer = models.ForeignKey('users.User', related_name='games_created')
    teams = models.ManyToManyField(Team, related_name='games')
    players = models.ManyToManyField('users.User', related_name='games',
                                     through='RsvpStatus')

    def __str__(self):
        return f'Game(datetime={self.datetime!r}, location={self.location})'

    class Meta:
        ordering = ['datetime']

    @staticmethod
    def get_cuttoff_time():
        """
        More often then not we don't care about games in the past. This
        method returns datetime to use in a query with datetime__gt filter
        """
        return datetime.utcnow() - timedelta(minutes=90)

    class GameQuerySet(models.QuerySet):
        """Support "future" games query filter"""
        def future(self):
            return self.filter(datetime__gt=Game.get_cuttoff_time())

    class GameManager(models.Manager):
        """Support "future" games query filter"""
        def get_queryset(self):
            return Game.GameQuerySet(self.model, using=self.db)

        def future(self):
            return self.get_queryset().future()

    objects = GameManager()


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
    player = models.ForeignKey('users.User', related_name='rsvps')
    status = models.IntegerField(choices=RSVP_CHOICES, default=INVITED)
    team = models.IntegerField(default=NO_TEAM)

    class Meta:
        unique_together = 'player', 'game'
        ordering = ['game__datetime']
        verbose_name = 'RSVP status'
        verbose_name_plural = 'RSVP statuses'
