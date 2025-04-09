from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from api.permissions import IsCorrectUser
from user.helpers import send_email_verification, build_verification_url
from user.models import User
from user.serializers import UserSerializer, BlacklistTokenSerializer, PasswordResetSerializer, \
    ForgetPasswordSerializer, EmailVerifySerializer


class UserViewSet(UpdateModelMixin,
                  CreateModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    update: Update the given user.
    create: Create a new user.
    destroy: Delete the given user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "identification_code"
    permission_classes = []

    def get_permissions(self):
        """
        Define custom permissions for each action.

        :return: List of permissions.
        """
        if self.action in ["create",
                           "forget_password",
                           "reset_password",
                           "verify_email"]:
            return []
        else:
            return [IsCorrectUser()]

    def perform_create(self, serializer):
        """
        mark is_active as False
        :param serializer: Serializer instance
        :return: None
        """
        # Send email verification
        serializer.save(is_active=False)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)
        verification_url = build_verification_url(user)
        send_email_verification(email, verification_url)

    @action(methods=["post"],
            detail=False,
            serializer_class=ForgetPasswordSerializer,
            permission_classes=[], url_path="forget-password")
    def forget_password(self, request):
        """
        Email the user with a link to reset the password.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            return Response(
                {
                    "message": "Password reset instructions sent to your email."
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"],
            detail=False,
            serializer_class=PasswordResetSerializer,
            permission_classes=[],
            url_path="reset-password")
    def reset_password(self, request):
        """
        Reset the password.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Password reset successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"],
            detail=False,
            serializer_class=EmailVerifySerializer,
            permission_classes=[],
            url_path="verify-email")
    def verify_email(self, request):
        """
        Verify the email of the user.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Email verified successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    """
    API endpoint that allows the current user to be viewed.
    """
    permission_classes = [IsCorrectUser]

    def get(self, request):
        """
        Return the current user.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class BlacklistTokenView(APIView):
    """
    A View for blacklisting tokens and clearing cookies.
    """
    serializer_class = BlacklistTokenSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )