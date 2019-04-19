import os

# avialable cofig modules
DEV_CONFIG_MODULE = 'informatics_front.config.DevConfig'
TEST_CONFIG_MODULE = 'informatics_front.TestConfig'
PROD_CONFIG_MODULE = 'informatics_front.config.ProdConfig'

# env-config mapping
CONFIG_ENV_MODULES = {
    'development': DEV_CONFIG_MODULE,
    'testing': TEST_CONFIG_MODULE,
    'production': PROD_CONFIG_MODULE,
}


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

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                             'mysql+pymysql://user:12345@localhost/pynformatics')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # services
    INTERNAL_RMATICS_URL = os.getenv('INTERNAL_RMATICS_URL')

    # mailers
    MAIL_FROM = os.getenv('MAIL_FROM', '')
    GMAIL_USERNAME = os.getenv('GMAIL_USERNAME', '')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '')


class DevConfig(BaseConfig):
    DEBUG = True

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class ProdConfig(BaseConfig):
    ...


# Determine appropriate config class based on provided env var,
# failback to dev, if `FLASK_ENV` has invalid value.
ENV = os.getenv('FLASK_ENV', 'development')
CONFIG_MODULE = CONFIG_ENV_MODULES.get(ENV, DEV_CONFIG_MODULE)
