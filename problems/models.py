
from django.db import models


class Problem(models.Model):
    contest_id = models.PositiveIntegerField()
    index = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    rating = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    tags = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "problems_problem"
        constraints = [
            models.UniqueConstraint(
                fields=["contest_id", "index"],
                name="unique_cf_problem",
            )
        ]
        ordering = ["rating", "contest_id", "index"]

    def __str__(self):
        return f"{self.contest_id}{self.index}: {self.name}"

    @property
    def url(self):
        return (
            f"https://codeforces.com/problemset/problem/"
            f"{self.contest_id}/{self.index}"
        )
