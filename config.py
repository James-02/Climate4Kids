from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    """
    Base Configuration
    """
    SECRET_KEY = environ.get('SECRET_KEY')
    SMTP_EMAIL = environ.get('SMTP_EMAIL')
    SMTP_PASSWORD = environ.get('SMTP_PASSWORD')
    DEBUG = True
    TESTING = False
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class DevelopmentConfig(Config):
    """
    Development configuration
    """
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_TEST')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """
    Production configuration
    """
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI_TEST')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_ENV = 'production'
    DEBUG = False
    Testing = False
