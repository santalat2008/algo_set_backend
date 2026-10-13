from django.conf import settings
from django.db import models

from problems.models import Problem


class RandomProblemAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="random_problem_attempts",
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="random_attempts",
    )
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "practice_random_problem_attempt"
        ordering = ["-selected_at"]
        indexes = [
            models.Index(
                fields=["user", "-selected_at"],
                name="practice_user_selected_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user_id}: {self.problem}"
