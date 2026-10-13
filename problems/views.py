from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from codeforces.models import CodeforcesAccount
from .models import Problem
from .serializers import ProblemSerializer


class ProblemPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class ProblemListView(ListAPIView):
    serializer_class = ProblemSerializer
    pagination_class = ProblemPagination

    def get_queryset(self):
        user = self.request.user

        if not CodeforcesAccount.objects.filter(user=user).exists():
            raise PermissionDenied(
                "Avval Codeforces akkauntingizni ulang."
            )

        queryset = Problem.objects.all()

        rating_min = self.request.query_params.get("rating_min")
        rating_max = self.request.query_params.get("rating_max")
        search = self.request.query_params.get("search", "").strip()
        tag = self.request.query_params.get("tag", "").strip()

        if rating_min:
            try:
                rating_min = int(rating_min)
            except ValueError:
                raise serializers.ValidationError({
                    "rating_min": "Butun son kiriting."
                })

            queryset = queryset.filter(rating__gte=rating_min)

        if rating_max:
            try:
                rating_max = int(rating_max)
            except ValueError:
                raise serializers.ValidationError({
                    "rating_max": "Butun son kiriting."
                })

            queryset = queryset.filter(rating__lte=rating_max)

        if (
            isinstance(rating_min, int)
            and isinstance(rating_max, int)
            and rating_min > rating_max
        ):
            raise serializers.ValidationError({
                "rating_max": "rating_min dan kichik bo'lmasligi kerak."
            })

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(index__icontains=search)
            )

        if tag:
            matching_ids = [
                problem.id
                for problem in queryset.only("id", "tags").iterator()
                if any(
                    tag.casefold() in str(problem_tag).casefold()
                    for problem_tag in (problem.tags or [])
                )
            ]
            queryset = queryset.filter(id__in=matching_ids)

        return queryset.order_by("rating", "contest_id", "index")
