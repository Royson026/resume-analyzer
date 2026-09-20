from django.db import models
from django.contrib.auth.models import User


class LoginActivity(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_activities"
    )

    logged_in_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.logged_in_at}"
        )