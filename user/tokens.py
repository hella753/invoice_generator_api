from django.contrib.auth.tokens import PasswordResetTokenGenerator

from user.models import User


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp):
        # Include email and active status in the hash
        return (
            str(user.pk) + str(timestamp) +
            str(user.email) + str(user.is_active)
        )


email_token_generator = EmailVerificationTokenGenerator()
