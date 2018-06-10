import os
from datetime import timedelta


def load_config():
    config_class = get_config_class()
    return config_class


def get_config_class():
    environment = os.environ.get('ENVIRONMENT', 'development')

    env_config_class_name = '{}Config'.format(environment.capitalize())

    import sys
    config_module = sys.modules[__name__]

    config_class = getattr(config_module, env_config_class_name)
    return config_class


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_EXPIRATION_DELTA = timedelta(seconds=300)


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://minesweeper@localhost:5432/minesweeper'
    DEVELOPMENT = True
    DEBUG = True
    JWT_EXPIRATION_DELTA = timedelta(seconds=6000)
