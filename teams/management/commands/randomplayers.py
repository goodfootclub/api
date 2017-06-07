"""Add randomly generated players in randomly generated teams
"""
from random import sample, randrange

from django.core.management.base import BaseCommand, CommandError

from teams.models import Team, Role
from users.models import User
from .randomteams import INFO_PREFIX
from users.management.commands.randomusers import USERNAME_PREFIX


def get_team_size():
    """Random team size:

    60% - 11 players with 3-4 subs
    40% - 8 players with 3-4 subs
    """
    return 11 if randrange(5) > 1 else 8, randrange(3, 5)


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        teams = Team.objects.filter(info__startswith=INFO_PREFIX)
        players = User.objects.filter(username__startswith=USERNAME_PREFIX)
        female_players = list(players.filter(gender=User.FEMALE))
        male_players = list(players.filter(gender=User.MALE))
        all_players = male_players + female_players

        for team in teams:
            current_members = team.players.all()
            if current_members.count() > 8:
                self.stdout.write(
                    'Enough players in the team "{}"'.format(team.name)
                )
                continue

            team.players.clear()

            players_wanted, subs_wanted = get_team_size()
            self.stdout.write(
                'Adding {} players and {} subs to the team "{}"'
                .format(players_wanted, subs_wanted, team.name)
            )

            if team.type == team.MALE:
                candidates = male_players
            if team.type == team.FEMALE:
                candidates = female_players
            if team.type == team.COED:
                candidates = all_players

            new_members = sample(candidates, players_wanted + subs_wanted)
            new_players = new_members[:players_wanted]
            new_subs = new_members[players_wanted:]

            team.managers.add(new_players[0])

            for player in new_players[1:]:
                Role(player=player, team=team, role=Role.FIELD).save()

            for player in new_subs:
                Role(player=player, team=team, role=Role.SUBSTITUTE).save()
