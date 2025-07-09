
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:Bhuvvi%40511@localhost/real_estate_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_change_me'
    LANGUAGES = {'en': 'English', 'kn': 'Kannada', 'te': 'Telugu'}