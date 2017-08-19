from django.contrib.auth.models import AbstractUser
from django.db import models
from timezone_field import TimeZoneField

from games.models import RsvpStatus
from teams.models import Role


class User(AbstractUser):
    """Default django user with some custom fields:

    Fields (in addition to the defaults):
        bio (Text) - "about me" summary
        birthday (Date) - date of birth to calculate age
        cover (Image) - profile cover image
        gender (String) - 'M' or 'F' to look up in the search
        img (Image) - profile picture
        phone (String) - phone number
        profile_complete (Bool) - profile is complete flag
        timezone (Timezone) - users timezone
    """
    FEMALE = 'F'
    MALE = 'M'

    GENDER_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    bio = models.TextField(null=True, blank=True, max_length=1000)
    birthday = models.DateField(null=True)
    cover = models.ImageField(null=True)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    img = models.ImageField(null=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    profile_complete = models.BooleanField(default=False)
    timezone = TimeZoneField(default='UTC')

    class Meta(AbstractUser.Meta):
        pass

    def get_invites_counts(self):
        """Get counts of pending game and team invitations

        player.get_invites_counts() -> (total, games, teams)
        """
        game_invites = self.rsvps.filter(status=RsvpStatus.INVITED).count()
        team_invites = self.role_set.filter(role=Role.INVITED).count()

        return game_invites + team_invites, game_invites, team_invites

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()

        if self.email != '' and User.objects.filter(email=self.email).count():
            # f'The email {self.email} is already in use. Will be set to blank'
            self.email = ''
        return super().save(*args, **kwargs)
