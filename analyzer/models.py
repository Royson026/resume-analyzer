from django.db import models
from django.contrib.auth.models import User


class ResumeAnalysis(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="resume_analyses"
    )

    resume_name = models.CharField(
        max_length=255
    )

    field = models.CharField(
        max_length=100,
        default="Other"
    )

    score = models.IntegerField()

    match_score = models.IntegerField(
        null=True,
        blank=True
    )

    skills = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.resume_name