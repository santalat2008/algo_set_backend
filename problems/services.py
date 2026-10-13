from django.db import transaction
from django.utils import timezone

from codeforces.services import fetch_problems
from .models import Problem


@transaction.atomic
def sync_problems() -> int:
    api_problems = fetch_problems()
    synced_at = timezone.now()
    objects = {}

    for item in api_problems:
        contest_id = item.get("contestId")
        index = item.get("index")
        name = item.get("name")

        if contest_id is None or not index or not name:
            continue

        problem = Problem(
            contest_id=contest_id,
            index=index,
            name=name,
            rating=item.get("rating"),
            tags=item.get("tags", []),
            updated_at=synced_at,
        )
        objects[(contest_id, index)] = problem

    Problem.objects.bulk_create(
        objects.values(),
        update_conflicts=True,
        unique_fields=["contest_id", "index"],
        update_fields=["name", "rating", "tags", "updated_at"],
        batch_size=1000,
    )

    return len(objects)
