import os


class BaseConfig:
    # global
    DEBUG = False
    TESTING = False

    # instance
    SERVER_NAME = os.getenv('SERVER_NAME', None)
    PREFERRED_URL_SCHEME = os.getenv('URL_SCHEME ', None)
    APP_URL = os.getenv('APP_URL', 'http://localhost')

    # secrets
    SECRET_KEY = os.getenv('SECRET_KEY', 'ZlXRrZypKWulCQuaMTdhkppPJSQXMRIqoFVMkqvHD5jbbYNO')
    ACTION_SECRET_KEY = os.getenv('ACTION_SECRET_KEY', 'pEdQsmKFzutMXp7TefrkbEddfgDOFqDgcFyUdofPJyEYqAfI')

    # auth
    JWT_TOKEN_EXP = 15 * 60
    JWT_REFRESH_TOKEN_EXP = 10 * 24 * 60

    # databases
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://user:12345@localhost/test')
    URL_ENCODER_ALPHABET = os.getenv('URL_ENCODER_ALPHABET', 'abcdefghijkl')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'mysql+pymysql://root:pass123@localhost:33066/informatics')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # services
    INTERNAL_RMATICS_URL = os.getenv('INTERNAL_RMATICS_URL')

    # mailers
    MAIL_FROM = os.getenv('MAIL_FROM', '')
    GMAIL_USERNAME = os.getenv('GMAIL_USERNAME', '')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '')

    # ejudge
    JUDGES_PATH = '/home/judges/'



class DevConfig(BaseConfig):
    ...


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False


class ProdConfig(BaseConfig):
    SQLALCHEMY_ECHO = False
