from django.db import models

from users.models import User


class Team(models.Model):
    """Team

    Fields:
        managers (MtM) - Users with permission to edit or delete the team
        name (String) - unique name of a team
        players (MtM) - Team members, each with a role (see Role)
    """
    managers = models.ManyToManyField(User, related_name='managed_teams')
    name = models.CharField(max_length=255, unique=True)
    players = models.ManyToManyField(User, related_name='teams',
                                     through='Role')

    def __str__(self):
        return "{name}".format(name=self.name)


class Role(models.Model):
    """Role of a player in a Team (captain, field, substitute, etc...)
    """
    # Active
    CAPTAIN = 3
    FIELD = 2
    SUBSTITUTE = 1

    # Inactive
    INACTIVE = 0
    INVITED = -1
    REQUESTED_TO_JOIN = -2

    CHOICES = (
        (CAPTAIN, 'Captain'),
        (FIELD, 'Field player'),
        (INACTIVE, 'Inactive'),
        (INVITED, 'Invited'),
        (REQUESTED_TO_JOIN, 'Asked to join'),
        (SUBSTITUTE, 'Substitute'),
    )

    player = models.ForeignKey(User)
    role = models.IntegerField(choices=CHOICES, default=INVITED)
    team = models.ForeignKey(Team)

    class Meta:
        unique_together = 'player', 'team'
        ordering = ['-role']
