from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    PURPOSE_CHOICES = (("register", "register"),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="register")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    @classmethod
    def create_for_user(cls, user, minutes=10):
        import secrets
        code = f"{secrets.randbelow(1000000):06d}"
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=minutes),
        )

    def valid(self, code):
        if self.is_used:
            return False, "OTP already used"
        if timezone.now() > self.expires_at:
            return False, "OTP expired"
        if self.code != code:
            return False, "Invalid OTP"
        return True, ""
