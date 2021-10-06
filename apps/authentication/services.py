from datetime import timedelta
from django.core import mail
from rest_framework_simplejwt.tokens import RefreshToken


class EmailToken(RefreshToken):
    lifetime = timedelta(minutes=2)


class Email:
    @staticmethod
    def send_email(subject, body, to, **kwargs):
        email_message = mail.EmailMessage(subject=subject, body=body, to=to, **kwargs)
        email_message.send()

    @staticmethod
    def create_email_token(user):
        token = EmailToken().for_user(user)
        return token

