from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from user.helpers import (send_reset_email, validate_passwords,
                          send_email_verification, build_verification_url, build_password_reset_url)
from user.models import User
from user.tokens import email_token_generator


class UserSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["receiver_name_ka",
                  "receiver_name_en",
                  "identification_code",
                  "email",
                  "bank_name_en",
                  "bank_name_ka",
                  "address",
                  "bank_code",
                  "bank_account_number",
                  "phone_number",
                  "current_password",
                  "password",
                  "confirm_password"]
        extra_kwargs = {
            "receiver_name_en": {"required": False},
            "bank_name_en": {"required": False},
            "password": {"write_only": True, "required": False},
            "address": {"required": False},
            "current_password": {"write_only": True, "required": False},
            "phone_number": {"required": False},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def validate(self, attrs):
        """
        Validate password and confirm_password fields.

        :param attrs: data to validate

        :return: validated data
        """
        # For new user creation
        if not self.instance:
            if not attrs.get("password"):
                raise serializers.ValidationError(
                    {"password": "This field is required."}
                )
            if not attrs.get("confirm_password"):
                raise serializers.ValidationError(
                    {"confirm_password": "This field is required."}
                )

        current_password = attrs.get("current_password", None)
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)

        # Password validation for both creation and update
        if password:
            # For existing user updating password
            if self.instance:
                if not current_password:
                    raise serializers.ValidationError(
                        {"current_password": "This field is required."}
                    )
                if not self.instance.check_password(current_password):
                    raise serializers.ValidationError(
                        {"current_password": "Incorrect password."}
                    )

            # Common validation
            if not confirm_password:
                raise serializers.ValidationError(
                    {"confirm_password": "This field is required."}
                )
            if password != confirm_password:
                raise serializers.ValidationError(
                    {"password": "Passwords do not match."}
                )
            validate_password(password)
        return attrs

    def create(self, validated_data):
        """
        Create a new user.

        :param validated_data: Validated data

        :return: New user
        """
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create user: {str(e)}"
            )

    def update(self, instance, validated_data):
        """
        Update an existing user.

        :param instance: Instance to update
        :param validated_data: Validated data

        :return: Updated user
        """
        password = validated_data.pop("password", None)
        old_email = instance.email
        email = validated_data.get("email", None)

        # Update user attributes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Set new password if provided
        if password:
            instance.set_password(password)

        if email != old_email:
            instance.is_active = False
            instance.save()
            verification_url = build_verification_url(instance)
            send_email_verification(email, verification_url)
        else:
            instance.save()
        return instance


class BlacklistTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        refresh_token = data.get('refresh')

        if not refresh_token:
            raise ValidationError("Refresh token is required.")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise ValidationError(f"Invalid token or blacklisting failed: {str(e)}")
        return data


class ForgetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("Email does not exist.")
        return email

    def save(self, request):
        email = self.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            reset_url = build_password_reset_url(user)
            send_reset_email([email], reset_url)
            return user
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to process password reset: {str(e)}"
            )


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    confirm_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    uid = serializers.CharField(write_only=True, required=False)
    token = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        uid = data.get("uid")
        token = data.get("token")

        if not uid or not token:
            raise serializers.ValidationError("Both UID and token are required.")

        try:
            uid = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid token.")

        try:
            validate_passwords(new_password, confirm_password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": str(e)})
        return data

    def save(self):
        uid = self.validated_data["uid"]
        user = User.objects.get(
            pk=urlsafe_base64_decode(uid)
        )
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class EmailVerifySerializer(serializers.Serializer):
    uid = serializers.CharField(write_only=True, required=False)
    token = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        uid = data.get("uid")
        token = data.get("token")

        if not uid or not token:
            raise serializers.ValidationError("Missing uid or token.")

        try:
            uid = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")

        if not email_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid token.")
        return data

    def save(self):
        try:
            uid = self.validated_data["uid"]
            user = User.objects.get(
                pk=urlsafe_base64_decode(uid)
            )
            user.is_active = True
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to verify email: {str(e)}"
            )