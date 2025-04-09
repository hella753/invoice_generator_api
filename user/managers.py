from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self,
                    receiver_name_ka,
                    identification_code,
                    email,
                    password,
                    **extra_fields):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            receiver_name_ka=receiver_name_ka,
            identification_code=identification_code,
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            receiver_name_ka,
            identification_code,
            email,
            password,
            **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            receiver_name_ka=receiver_name_ka,
            identification_code=identification_code,
            email=email,
            password=password,
            **extra_fields
        )