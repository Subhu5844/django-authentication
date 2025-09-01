from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, v):
        if User.objects.filter(email__iexact=v, is_active=True).exists():
            raise serializers.ValidationError("User already exists.")
        return v


class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# ---------- Added below to make Swagger show bodies clearly ----------

class MessageSerializer(serializers.Serializer):
    """Uniform {'detail': '...'} for success/error messages."""
    detail = serializers.CharField()


class EmptySerializer(serializers.Serializer):
    """Use for endpoints that accept an empty body (still shows a body box in Swagger)."""
    pass


class MeResponseSerializer(serializers.Serializer):
    """Shape of GET /api/me/ response."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()
    date_joined = serializers.DateTimeField()
    is_active = serializers.BooleanField()
