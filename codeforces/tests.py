from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import CodeforcesAccount, CodeforcesSubmission
from .submission_services import sync_user_submissions
from types import SimpleNamespace

from .submission_services import get_solved_problem_keys, is_problem_solved

User = get_user_model()


class CodeforcesConnectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = "/api/v1/codeforces/connect/"

    @patch("codeforces.views.fetch_user_info")
    def test_connect_valid_handle(self, mock_fetch):
        mock_fetch.return_value = {
            "handle": "tourist",
            "rating": 3800,
            "maxRating": 3979,
            "rank": "legendary grandmaster",
            "maxRank": "legendary grandmaster",
            "contribution": 100,
            "friendOfCount": 5000,
        }

        response = self.client.post(
            self.url,
            {"handle": "tourist"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["handle"], "tourist")
        self.assertEqual(response.data["rating"], 3800)
        self.assertTrue(
            CodeforcesAccount.objects.filter(user=self.user).exists()
        )

    def test_connect_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {"handle": "tourist"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)


class SubmissionSyncTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="submission_user",
            email="submission@example.com",
            password="TestPass123!",
        )
        self.account = CodeforcesAccount.objects.create(
            user=self.user,
            handle="tourist_test",
            rating=1500,
        )

    @patch("codeforces.submission_services.fetch_user_submissions")
    def test_sync_saves_submission(self, mock_fetch):
        mock_fetch.return_value = [
            {
                "id": 987654321,
                "creationTimeSeconds": 1700000000,
                "verdict": "OK",
                "programmingLanguage": "GNU C++20",
                "problem": {
                    "contestId": 1000,
                    "index": "A",
                },
            }
        ]

        count = sync_user_submissions(self.account)

        self.assertEqual(count, 1)
        self.assertEqual(CodeforcesSubmission.objects.count(), 1)

        submission = CodeforcesSubmission.objects.get(
            submission_id=987654321
        )
        self.assertEqual(submission.account, self.account)
        self.assertEqual(submission.verdict, "OK")
        self.assertEqual(submission.contest_id, 1000)
        self.assertEqual(submission.problem_index, "A")

    @patch("codeforces.submission_services.fetch_user_submissions")
    def test_sync_does_not_duplicate_existing_submission(self, mock_fetch):
        mock_fetch.return_value = [
            {
                "id": 987654322,
                "creationTimeSeconds": 1700000000,
                "verdict": "OK",
                "programmingLanguage": "GNU C++20",
                "problem": {
                    "contestId": 1000,
                    "index": "B",
                },
            }
        ]

        sync_user_submissions(self.account)
        sync_user_submissions(self.account)

        self.assertEqual(
            CodeforcesSubmission.objects.filter(
                submission_id=987654322
            ).count(),
            1,
        )

    @patch("codeforces.submission_services.fetch_user_submissions")
    def test_sync_skips_submission_with_missing_problem_data(
        self, mock_fetch
    ):
        mock_fetch.return_value = [
            {
                "id": 987654323,
                "creationTimeSeconds": 1700000000,
                "verdict": "OK",
                "problem": {},
            }
        ]

        count = sync_user_submissions(self.account)

        self.assertEqual(count, 0)
        self.assertEqual(CodeforcesSubmission.objects.count(), 0)

    @patch("codeforces.submission_services.fetch_user_submissions")
    def test_sync_updates_last_synced_at(self, mock_fetch):
        mock_fetch.return_value = []

        self.assertIsNone(self.account.last_synced_at)

        sync_user_submissions(self.account)

        self.account.refresh_from_db()
        self.assertIsNotNone(self.account.last_synced_at)

    @patch(
        "codeforces.submission_services.fetch_user_submissions",
        side_effect=Exception("Network error"),
    )
    def test_api_failure_does_not_create_submissions(self, mock_fetch):
        with self.assertRaises(Exception):
            sync_user_submissions(self.account)

        self.assertEqual(CodeforcesSubmission.objects.count(), 0)

class SolvedProblemTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="solved_user",
            email="solved@example.com",
            password="TestPass123!",
        )
        self.account = CodeforcesAccount.objects.create(
            user=self.user,
            handle="solved_test",
            rating=1200,
        )

    def test_only_ok_submissions_count_as_solved(self):
        CodeforcesSubmission.objects.create(
            account=self.account,
            submission_id=111,
            contest_id=1000,
            problem_index="A",
            verdict="OK",
            submitted_at=__import__("django.utils.timezone", fromlist=["now"]).now(),
        )
        CodeforcesSubmission.objects.create(
            account=self.account,
            submission_id=112,
            contest_id=1000,
            problem_index="B",
            verdict="WRONG_ANSWER",
            submitted_at=__import__("django.utils.timezone", fromlist=["now"]).now(),
        )

        solved = get_solved_problem_keys(self.account)

        self.assertEqual(solved, {(1000, "A")})

    def test_is_problem_solved(self):
        from problems.models import Problem
        from django.utils import timezone

        problem = Problem.objects.create(
            contest_id=1000,
            index="A",
            name="Test",
            rating=1200,
            tags=["implementation"],
        )

        CodeforcesSubmission.objects.create(
            account=self.account,
            submission_id=113,
            contest_id=1000,
            problem_index="A",
            verdict="OK",
            submitted_at=timezone.now(),
        )

        self.assertTrue(is_problem_solved(self.account, problem))