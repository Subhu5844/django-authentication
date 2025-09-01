from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(to_email: str, code: str):
    subject = "Your OTP Code"
    body = f"Your verification code is: {code}\nThis code expires in 10 minutes."
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
