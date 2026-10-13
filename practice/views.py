from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from codeforces.models import CodeforcesAccount
from .serializers import RandomProblemAttemptSerializer
from .services import choose_random_problem, get_latest_random_problem


class RandomProblemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not CodeforcesAccount.objects.filter(user=request.user).exists():
            raise PermissionDenied("Avval Codeforces akkauntingizni ulang.")

        attempt = get_latest_random_problem(request.user)

        if attempt is None:
            return Response(
                {"detail": "Hali masala tanlanmagan. Yangi masala so'rang."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(RandomProblemAttemptSerializer(attempt).data)


    def post(self, request):
        if not CodeforcesAccount.objects.filter(user=request.user).exists():
            raise PermissionDenied(
                "Avval Codeforces akkauntingizni ulang."
            )

        try:
            attempt = choose_random_problem(request.user)
        except ValueError as exc:
            raise PracticeUnavailable(str(exc)) from exc

        return Response(
            RandomProblemAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )

class PracticeUnavailable(APIException):
    status_code = 503
    default_detail = (
        "Hozir masala tanlab bo'lmaydi. "
        "Masalalar katalogini sinxronlang."
    )
    default_code = "practice_unavailable"
