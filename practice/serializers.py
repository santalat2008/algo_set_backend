from rest_framework import serializers

from problems.serializers import ProblemSerializer
from .models import RandomProblemAttempt


class RandomProblemAttemptSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)

    class Meta:
        model = RandomProblemAttempt
        fields = ("id", "problem", "selected_at")
