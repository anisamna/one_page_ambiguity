from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q


class EmailBackend(BaseBackend):
    """
    Custom Email Backend to perform authentication via email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(Q(email=username) | Q(username=username))
            if user.check_password(password):  # check valid password
                return user  # return user to be authenticated
            return None
        except user_model.DoesNotExist:  # no matching user exists
            return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
