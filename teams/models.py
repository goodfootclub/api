from datetime import datetime, timedelta

from django.db import models
from django.db.transaction import atomic


class Team(models.Model):
    """Team

    Fields:
        info (String) - team description
        managers (MtM) - Users with permission to edit or delete the team
        name (String) - unique name of a team
        players (MtM) - Team members, each with a role (see Role)
        slots_female (Int) - number of female players wanted more
        slots_male (Int) - number of male players wanted more
        type (Int) - Team type by players gender (Coed/Female/Male)
    """
    # Team players gender preference
    COED = 0
    FEMALE = 1
    MALE = 2

    TYPE_CHOICES = (
        (COED, 'Coed'),
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    info = models.CharField(max_length=1000, null=True, blank=True)
    managers = models.ManyToManyField('users.User', related_name='managed_teams')
    name = models.CharField(max_length=30)
    players = models.ManyToManyField('users.User', related_name='teams',
                                     through='Role')
    slots_female = models.IntegerField(null=True, default=0)
    slots_male = models.IntegerField(null=True, default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, default=COED)

    def __str__(self):
        return "{name}".format(name=self.name)


class Role(models.Model):
    """Role of a player in a Team (captain, field, substitute, etc...)"""
    # Active
    CAPTAIN = 3
    FIELD = 2
    SUBSTITUTE = 1

    # Inactive
    INACTIVE = 0
    INVITED = -1
    REQUESTED_TO_JOIN = -2

    ROLE_CHOICES = (
        (CAPTAIN, 'Captain'),
        (FIELD, 'Field player'),
        (INACTIVE, 'Inactive'),
        (INVITED, 'Invited'),
        (REQUESTED_TO_JOIN, 'Asked to join'),
        (SUBSTITUTE, 'Substitute'),
    )

    player = models.ForeignKey('users.User')
    role = models.IntegerField(choices=ROLE_CHOICES, default=INVITED)
    team = models.ForeignKey(Team)

    class Meta:
        unique_together = 'player', 'team'
        ordering = ['-role']

    @atomic
    def save(self, *args, **kwargs):
        new = self.id is None
        role = super().save(*args, **kwargs)

        if new:
            # New player. Let's add him to existing games
            # FIXME: can't import at the top (circular imports)
            from games.models import RsvpStatus
            games = self.team.games.filter(datetime__gt=datetime.utcnow())

            for game in games:
                RsvpStatus.objects.get_or_create(
                    game=game,
                    player=self.player,
                    status=RsvpStatus.INVITED,
                )

        return role
