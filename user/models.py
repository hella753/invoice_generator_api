from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    receiver_name_ka = models.CharField(max_length=100)
    receiver_name_en = models.CharField(max_length=100, blank=True, null=True)
    identification_code = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=100)
    bank_name_en = models.CharField(max_length=100, blank=True, null=True)
    bank_name_ka = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=100)

    REQUIRED_FIELDS = ['receiver_name_ka',
                       'identification_code',
                       'password']

    USERNAME_FIELD = 'email'
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name="staff status"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="active status"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="superuser status"
    )
    objects = UserManager()

    def __str__(self):
        return self.receiver_name_ka