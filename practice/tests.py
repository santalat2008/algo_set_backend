from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from codeforces.models import CodeforcesAccount
from problems.models import Problem
from .models import RandomProblemAttempt
from codeforces.models import CodeforcesAccount, CodeforcesSubmission

User = get_user_model()


class RandomProblemAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
        )
        self.client = APIClient()
        self.url = "/api/v1/practice/random-problem/"

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def connect_codeforces(self, rating=1200):
        return CodeforcesAccount.objects.create(
            user=self.user,
            handle="test_handle",
            rating=rating,
        )

    def create_problem(
        self,
        contest_id=1000,
        index="A",
        name="Test Problem",
        rating=1200,
        tags=None,
    ):
        return Problem.objects.create(
            contest_id=contest_id,
            index=index,
            name=name,
            rating=rating,
            tags=tags or [],
        )

    def test_random_problem_requires_authentication(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_random_problem_requires_connected_codeforces_account(self):
        self.authenticate()

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(RandomProblemAttempt.objects.count(), 0)

    def test_post_selects_and_saves_random_problem(self):
        self.authenticate()
        self.connect_codeforces(rating=1200)
        problem = self.create_problem(rating=1200)

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(response.data["problem"]["id"], problem.id)
        self.assertEqual(RandomProblemAttempt.objects.count(), 1)
        self.assertEqual(
            RandomProblemAttempt.objects.get().user,
            self.user,
        )

    def test_get_returns_latest_selected_problem(self):
        self.authenticate()
        self.connect_codeforces()
        first_problem = self.create_problem(
            contest_id=1001,
            index="A",
            name="First Problem",
        )
        latest_problem = self.create_problem(
            contest_id=1002,
            index="B",
            name="Latest Problem",
        )

        RandomProblemAttempt.objects.create(
            user=self.user,
            problem=first_problem,
        )
        latest_attempt = RandomProblemAttempt.objects.create(
            user=self.user,
            problem=latest_problem,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["id"],
            latest_attempt.id,
        )
        self.assertEqual(
            response.data["problem"]["id"],
            latest_problem.id,
        )

    def test_get_returns_404_when_no_problem_was_selected(self):
        self.authenticate()
        self.connect_codeforces()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_selects_problem_near_user_rating(self):
        self.authenticate()
        self.connect_codeforces(rating=1200)

        matching_problem = self.create_problem(
            contest_id=2001,
            index="A",
            rating=1200,
        )
        self.create_problem(
            contest_id=2002,
            index="A",
            rating=2000,
        )

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["problem"]["id"],
            matching_problem.id,
        )

    def test_new_selection_is_saved_in_history(self):
        self.authenticate()
        self.connect_codeforces()
        self.create_problem()

        self.client.post(self.url)
        self.client.post(self.url)

        self.assertEqual(RandomProblemAttempt.objects.count(), 2)


    def test_empty_problem_catalog_returns_503(self):
        self.authenticate()
        self.connect_codeforces()

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )


    def test_random_problem_skips_solved_problems(self):
        self.authenticate()
        account = self.connect_codeforces(rating=1200)

        solved_problem = self.create_problem(
            contest_id=3001,
            index="A",
            name="Already Solved",
            rating=1200,
        )
        unsolved_problem = self.create_problem(
            contest_id=3002,
            index="A",
            name="Not Solved",
            rating=1200,
        )

        CodeforcesSubmission.objects.create(
            account=account,
            submission_id=987650001,
            contest_id=solved_problem.contest_id,
            problem_index=solved_problem.index,
            verdict="OK",
            submitted_at=timezone.now(),
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["problem"]["id"],
            unsolved_problem.id,
        )
        self.assertNotEqual(
            response.data["problem"]["id"],
            solved_problem.id,
        )

    def test_returns_503_when_all_matching_problems_are_solved(self):
        self.authenticate()
        account = self.connect_codeforces(rating=1200)

        problem = self.create_problem(
            contest_id=3003,
            index="A",
            name="Solved Problem",
            rating=1200,
        )

        CodeforcesSubmission.objects.create(
            account=account,
            submission_id=987650002,
            contest_id=problem.contest_id,
            problem_index=problem.index,
            verdict="OK",
            submitted_at=timezone.now(),
        )

        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(RandomProblemAttempt.objects.count(), 0)
