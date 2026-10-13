from rest_framework import serializers

from .models import Problem


class ProblemSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Problem
        fields = (
            "id",
            "contest_id",
            "index",
            "name",
            "rating",
            "tags",
            "url",
        )
