from django.db import transaction

from codeforces.models import CodeforcesAccount
from codeforces.submission_services import get_solved_problem_keys
from problems.models import Problem

from .models import RandomProblemAttempt

@transaction.atomic
def choose_random_problem(user):
    account = CodeforcesAccount.objects.filter(user=user).first()

    if account is None:
        raise ValueError("Avval Codeforces akkauntingizni ulang.")

    if account.rating is None:
        min_rating, max_rating = 800, 1200
    else:
        min_rating = max(0, account.rating - 200)
        max_rating = account.rating + 200

    solved_keys = get_solved_problem_keys(account)
    solved_problem_ids = []

    if solved_keys:
        # Yechilgan masalalarni katalogdan chiqaramiz.
        # Buni DB so'rovida bosqichma-bosqich bajarish uchun
        # solved masalalar IDlarini olamiz.
        solved_problem_ids = list(
            Problem.objects.filter(
                contest_id__in=[key[0] for key in solved_keys]
            ).values_list("id", "contest_id", "index")
        )
        solved_ids = [
            problem_id
            for problem_id, contest_id, index in solved_problem_ids
            if (contest_id, index) in solved_keys
        ]
    else:
        solved_ids = []

    queryset = Problem.objects.filter(
        rating__gte=min_rating,
        rating__lte=max_rating,
    ).exclude(id__in=solved_ids)

    recent_ids = list(
        RandomProblemAttempt.objects.filter(user=user)
        .order_by("-selected_at")
        .values_list("problem_id", flat=True)[:10]
    )

    fresh_queryset = queryset.exclude(id__in=recent_ids)
    problem = fresh_queryset.order_by("?").first()

    if problem is None:
        problem = queryset.order_by("?").first()

    if problem is None:
        raise ValueError(
            "Mos, hali yechilmagan masala topilmadi."
        )

    return RandomProblemAttempt.objects.create(
        user=user,
        problem=problem,
    )

def get_latest_random_problem(user):
    return (
        RandomProblemAttempt.objects
        .filter(user=user)
        .select_related("problem")
        .first()
    )
