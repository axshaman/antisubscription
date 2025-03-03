# -*- coding: utf-8 -*-
import os
import dotenv



dotenv.load_dotenv()
# === YANDEX ===
MAIL_SERVICE = os.getenv('mail_service')
MAIL_LOGIN = os.getenv('login')
MAIL_PASSWORD = os.getenv('password')
# === GMAIL ===
MAIL_SERVICE_GMAIL = os.getenv('mail_service_gmail')
MAIL_LOGIN_GMAIL = os.getenv('login_gmail')
MAIL_PASSWORD_GMAIL = os.getenv('password_gmail')


# ----- Postgres -----
PG_LOGIN = os.getenv('user_login')
PG_PASSWORD = os.getenv('user_pass')


DEBUG = False
SECRET_KEY = 'asdfsdfssf asf dsgsdg'

# Database settings:
# SQLALCHEMY_DATABASE_URI = 'sqlite:///mails.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = False

