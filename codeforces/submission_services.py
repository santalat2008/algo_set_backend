from datetime import datetime, timezone as dt_timezone

from django.utils import timezone

from .models import CodeforcesSubmission
from .services import fetch_user_submissions


def sync_user_submissions(account) -> int:
    submissions = fetch_user_submissions(account.handle)
    objects = []

    for item in submissions:
        problem = item.get("problem") or {}
        contest_id = problem.get("contestId")
        problem_index = problem.get("index")
        submission_id = item.get("id")
        creation_time = item.get("creationTimeSeconds")

        if (
            submission_id is None
            or contest_id is None
            or not problem_index
            or creation_time is None
        ):
            continue

        submitted_at = datetime.fromtimestamp(
            creation_time,
            tz=dt_timezone.utc,
        )

        objects.append(
            CodeforcesSubmission(
                account=account,
                submission_id=submission_id,
                contest_id=contest_id,
                problem_index=problem_index,
                verdict=item.get("verdict", "") or "",
                programming_language=item.get("programmingLanguage", "") or "",
                submitted_at=submitted_at,
            )
        )

    CodeforcesSubmission.objects.bulk_create(
        objects,
        ignore_conflicts=True,
        batch_size=500,
    )

    account.last_synced_at = timezone.now()
    account.save(update_fields=["last_synced_at", "updated_at"])

    return len(objects)


def get_solved_problem_keys(account) -> set[tuple[int, str]]:
    return set(
        CodeforcesSubmission.objects.filter(
            account=account,
            verdict="OK",
        ).values_list("contest_id", "problem_index")
    )


def is_problem_solved(account, problem) -> bool:
    return CodeforcesSubmission.objects.filter(
        account=account,
        contest_id=problem.contest_id,
        problem_index=problem.index,
        verdict="OK",
    ).exists()
