import os

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    BOOTSTRAP_USE_MINIFIED = False