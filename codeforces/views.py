from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CodeforcesAccount
from .serializers import (
    CodeforcesAccountSerializer,
    ConnectCodeforcesSerializer,
)
from .services import CodeforcesAPIError, fetch_user_info

class CodeforcesUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Codeforces API vaqtincha ishlamayapti."
    default_code = "codeforces_unavailable"

class CodeforcesConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConnectCodeforcesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        handle = serializer.validated_data["handle"]

        try:
            profile = fetch_user_info(handle)
        except CodeforcesAPIError as exc:
            raise CodeforcesUnavailable(str(exc)) from exc

        defaults = {
            "rating": profile.get("rating"),
            "max_rating": profile.get("maxRating"),
            "rank": profile.get("rank", ""),
            "max_rank": profile.get("maxRank", ""),
            "contribution": profile.get("contribution", 0),
            "friend_of_count": profile.get("friendOfCount", 0),
            "last_synced_at": timezone.now(),
        }

        try:
            with transaction.atomic():
                account, created = CodeforcesAccount.objects.update_or_create(
                    user=request.user,
                    defaults={"handle": profile["handle"], **defaults},
                )
        except IntegrityError as exc:
            raise APIException(
                "Bu Codeforces akkaunti boshqa foydalanuvchiga ulangan."
            ) from exc

        response_serializer = CodeforcesAccountSerializer(account)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
