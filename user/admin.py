from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from user.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "receiver_name_ka", "receiver_name_en",
                    "is_active", "is_staff")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "receiver_name_ka", "receiver_name_en",
                     "identification_code")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("receiver_name_ka", "receiver_name_en",
                                      "identification_code")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "receiver_name_ka", "receiver_name_en",
                       "password1", "password2",
                       "is_active", "is_staff", "is_superuser"),
        }),
    )

