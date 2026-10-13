from django.conf import settings
from django.db import models


class CodeforcesAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="codeforces_account",
    )
    handle = models.CharField(max_length=24, unique=True)
    rating = models.IntegerField(null=True, blank=True)
    max_rating = models.IntegerField(null=True, blank=True)
    rank = models.CharField(max_length=32, blank=True)
    max_rank = models.CharField(max_length=32, blank=True)
    contribution = models.IntegerField(default=0)
    friend_of_count = models.PositiveIntegerField(default=0)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "codeforces_account"

    def __str__(self):
        return self.handle


class CodeforcesSubmission(models.Model):
    account = models.ForeignKey(
        CodeforcesAccount,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    submission_id = models.BigIntegerField(unique=True)
    contest_id = models.PositiveIntegerField()
    problem_index = models.CharField(max_length=10)
    verdict = models.CharField(max_length=32, blank=True)
    programming_language = models.CharField(max_length=64, blank=True)
    submitted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "codeforces_submission"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(
                fields=["account", "contest_id", "problem_index"],
                name="cf_sub_account_problem_idx",
            ),
        ]

    def __str__(self):
        return f"{self.account.handle}: {self.contest_id}{self.problem_index}"
