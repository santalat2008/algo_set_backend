from rest_framework import serializers

from .models import CodeforcesAccount


class ConnectCodeforcesSerializer(serializers.Serializer):
    handle = serializers.CharField(max_length=24, trim_whitespace=True)

    def validate_handle(self, value):
        if not value.strip():
            raise serializers.ValidationError("Handle bo'sh bo'lmasligi kerak.")
        return value.strip()


class CodeforcesAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeforcesAccount
        fields = (
            "handle",
            "rating",
            "max_rating",
            "rank",
            "max_rank",
            "last_synced_at",
        )
        read_only_fields = fields