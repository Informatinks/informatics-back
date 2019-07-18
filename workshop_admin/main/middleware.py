import hashlib

from django.contrib.auth import get_user_model

User = get_user_model()


class MoodleAccountAuthorization:
    def authenticate(self, _, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not all([username, password]):
            return None

        password_hash = hashlib.md5(str(password).encode('utf-8')).hexdigest()

        try:
            user = User.objects \
                .prefetch_related('roles') \
                .filter(username=username, password=password_hash).get()
        except User.DoesNotExist:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
