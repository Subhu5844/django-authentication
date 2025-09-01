from typing import Optional, Tuple
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication, CSRFCheck
from rest_framework import exceptions
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CookieTokenAuthentication(BaseAuthentication):
    """
    Reads 'auth_token' from cookies and authenticates against DRF's Token model.
    Enforces CSRF on unsafe methods (mirrors DRF's SessionAuthentication behavior).
    """

    def authenticate(self, request) -> Optional[Tuple[User, Token]]:
        token = request.COOKIES.get("auth_token")
        if not token:
            # No auth cookie -> let other authenticators (or permissions) decide.
            return None

        # For unsafe methods, enforce CSRF
        if request.method in UNSAFE_METHODS:
            # CSRFCheck (Django 5.x) requires a get_response callable
            check = CSRFCheck(lambda r: None)
            # Run the same hooks the middleware would
            check.process_request(request)
            reason = check.process_view(request, None, (), {})
            if reason:
                raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

        try:
            token_obj = Token.objects.select_related("user").get(key=token)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid auth cookie."))

        if not token_obj.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return token_obj.user, token_obj
