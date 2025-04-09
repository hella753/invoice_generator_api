import os

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.tokens import email_token_generator


def send_reset_email(recipient_list, url):
    """
    This function is used to email to the user with a
    link to reset their password.
    :param recipient_list: Recipient email addresses
    :param url: link to reset password
    """
    mail = EmailMessage(
        subject="Reset Password",
        body="You have requested to reset your password. "
             "Click the link below to reset your password.\n"
                f"{url}",
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list
    )
    mail.send(fail_silently=False)

def send_email_verification(email, url):
    """
    This function is used to email to the user with a
    link to verify their email.
    :param email: email address
    :param url: link to verify email
    """
    mail = EmailMessage(
        subject="Verify Email",
        body="Click the link below to verify your email.\n"
             f"{url}",
        from_email=settings.EMAIL_HOST_USER,
        to=[email]
    )
    mail.send(fail_silently=False)

def validate_passwords(new_password, confirm_password):
    """
    This function is used to validate the passwords.
    :param new_password: password
    :param confirm_password: confirm password
    """
    if new_password != confirm_password:
        raise serializers.ValidationError("Passwords do not match.")
    try:
        validate_password(new_password)
    except ValidationError as e:
        raise serializers.ValidationError({"password": e})

def build_verification_url(user):
    """
    Helper function to build the email verification URL
    """
    FRONTEND_URL = getattr(settings, 'FRONTEND_URL',
                           os.getenv('FRONTEND_URL', 'http://localhost:5500'))
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    return f"{FRONTEND_URL}/verify-email?token={token}&uid={uid}"

def build_password_reset_url(user):
    """
    Helper function to build the password reset URL
    """
    FRONTEND_URL = getattr(settings, 'FRONTEND_URL',
                           os.getenv('FRONTEND_URL', 'http://localhost:5500'))
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{FRONTEND_URL}/reset-password?token={token}&uid={uid}"