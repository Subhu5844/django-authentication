# Create your views here.
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import OTP
from .serializers import (
    RegisterSerializer,
    VerifySerializer,
    LoginSerializer,
    MessageSerializer,
    EmptySerializer,
    MeResponseSerializer,
)
from .emails import send_otp_email

COOKIE_NAME = "auth_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def _auth_cookie_kwargs(request):
    # respect HTTPS flags based on settings
    from django.conf import settings
    return dict(
        httponly=True,
        secure=False if settings.DEBUG else True,
        samesite="Lax",
        path="/",
        max_age=COOKIE_MAX_AGE,
    )


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    # Prevent a stale auth cookie from triggering custom authentication here
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(MessageSerializer, description="OTP sent to email"),
            400: OpenApiResponse(MessageSerializer, description="Validation error"),
            409: OpenApiResponse(MessageSerializer, description="User already active"),
        },
        examples=[
            OpenApiExample(
                "Example request",
                value={"email": "user@example.com", "password": "SecretPass123"},
                request_only=True,
            )
        ],
    )
    @transaction.atomic
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email, "is_active": False}
        )
        if not created and user.is_active:
            return Response({"detail": "User already active."}, status=409)

        user.username = email
        user.set_password(password)
        user.is_active = False
        user.save()

        # Invalidate previous unused OTPs
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)

        otp = OTP.create_for_user(user)
        send_otp_email(email, otp.code)

        return Response({"detail": "OTP sent to email."}, status=201)


class VerifyRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    # Same reason as above: no authentication should run here
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=VerifySerializer,
        responses={
            200: OpenApiResponse(MessageSerializer, description="Registration verified"),
            400: OpenApiResponse(MessageSerializer, description="Invalid/expired OTP"),
            404: OpenApiResponse(MessageSerializer, description="User not found"),
        },
        examples=[
            OpenApiExample(
                "Example request",
                value={"email": "user@example.com", "otp": "123456"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        ser = VerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        code = ser.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        otp = (
            OTP.objects.filter(user=user, purpose="register", is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp:
            return Response({"detail": "OTP not found."}, status=400)

        valid, reason = otp.valid(code)
        if not valid:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return Response({"detail": reason}, status=400)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"detail": "Registration verified."})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    # Allow unauthenticated access to login
    authentication_classes = []

    @extend_schema(
        tags=["Auth"],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(MessageSerializer, description="Logged in (cookie set)"),
            400: OpenApiResponse(MessageSerializer, description="Invalid credentials"),
        },
        examples=[
            OpenApiExample(
                "Example request",
                value={"email": "user@example.com", "password": "SecretPass123"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if not user or not user.is_active:
            return Response({"detail": "Invalid credentials."}, status=400)

        # rotate token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        resp = Response({"detail": "Logged in."})
        resp.set_cookie(COOKIE_NAME, token.key, **_auth_cookie_kwargs(request))

        # Ensure CSRF cookie exists (Swagger already sets it, but this helps with custom clients)
        from django.middleware.csrf import get_token
        get_token(request)  # ensures CSRF token is generated for this session
        return resp


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        responses={200: MeResponseSerializer},
    )
    def get(self, request):
        u = request.user
        return Response(
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "date_joined": u.date_joined,
                "is_active": u.is_active,
            }
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        request=EmptySerializer,  # shows an empty JSON body box in Swagger
        responses={200: OpenApiResponse(MessageSerializer, description="Logged out (cookie cleared)")},
        examples=[OpenApiExample("Empty body", value={}, request_only=True)],
    )
    def post(self, request):
        # delete token server-side
        Token.objects.filter(user=request.user).delete()

        resp = Response({"detail": "Logged out."})
        resp.delete_cookie(COOKIE_NAME, path="/", samesite="Lax")
        return resp
