from typing import Any

from itsdangerous import URLSafeTimedSerializer

DEFAULT_TOKEN_TTL = 86400  # 1 day


class BasePlugin:
    """Base class for Tokenizer deferred init"""

    def init_app(self, app):
        self.secret_key = app.config.get('ACTION_SECRET_KEY')
        self.serializer = URLSafeTimedSerializer(self.secret_key)


class Tokenizer(BasePlugin):
    def __init__(self, ttl: int = DEFAULT_TOKEN_TTL):
        self.secret_key = None
        self.serializer = None
        self.ttl = ttl

    def pack(self, payload: Any) -> str:
        """Returns signed token with encoded payload

        :param payload: Object to serialize into token
        :return: token string
        """
        return self.serializer.dumps(payload)

    def unpack(self, token: str = None, ttl: int = None) -> Any:
        """Returns decoded from encrypted token string Object

        Raises Exception both if token is invalid and if signature is expired
        :param token: encrypted token string
        :param ttl: per-call sets max signature expiration time in seconds
        :return: decoded object
        """
        return self.serializer.loads(token, max_age=(ttl or self.ttl))
