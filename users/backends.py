from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameAuthBackend(ModelBackend):
    """
    Allows use of either username or email.

    Thanks https://stackoverflow.com/a/35836674/723891
    """

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        # `username` field does not restring using `@`, so technically
        # email can be as username and email, even with different users
        users = UserModel._default_manager.filter(
            Q(**{UserModel.USERNAME_FIELD: username}) |
            Q(**{f'{UserModel.EMAIL_FIELD}__iexact': username})
        )
        # check for any password match
        for user in users:
            if user.check_password(password):
                return user
        if not users:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
