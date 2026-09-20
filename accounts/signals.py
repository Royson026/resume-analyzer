from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import LoginActivity


@receiver(user_logged_in)
def record_login(
    sender,
    request,
    user,
    **kwargs
):

    LoginActivity.objects.create(
        user=user
    )