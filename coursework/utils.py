# Reference: https://stackoverflow.com/questions/55005070/how-to-send-email-verification-link-in-django
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp: int):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_email_verified)
        )


generate_token = TokenGenerator()
