# -*- coding: utf-8 -*-
"""
config.py
=========
Configuration centralisée de l'application PDSC.
Les informations sensibles doivent être fournies
via des variables d'environnement.
"""

import os
from datetime import timedelta

from sqlalchemy.pool import NullPool


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# ============================================================
# .env - développement local
# ============================================================

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    pass


# ============================================================
# Détection de l'environnement Vercel (serverless)
# ============================================================

IS_VERCEL = bool(os.environ.get('VERCEL'))


def _normalize_db_url(url):
    """Adapte l'URL PostgreSQL de Supabase pour SQLAlchemy/psycopg2.

    - 'postgres://'  -> 'postgresql://'  (SQLAlchemy 1.4+ refuse 'postgres://')
    - retourne None si la variable est vide.
    """
    if not url:
        return None
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url


def _engine_options():
    """Options du moteur SQLAlchemy.

    Sur Vercel chaque invocation peut tourner dans une instance différente :
    on désactive le pool local (NullPool) et on laisse le pooler de Supabase
    (Supavisor, port 6543) gérer les connexions. SSL est exigé par Supabase.
    """
    options = {
        'pool_pre_ping': True,
        'connect_args': {'sslmode': os.environ.get('DB_SSLMODE', 'require')},
    }
    if IS_VERCEL:
        options['poolclass'] = NullPool
    return options


class Config:
    """Configuration commune à tous les environnements."""

    # ========================================================
    # Sécurité
    # ========================================================

    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'change-this-secret-key-in-production'
    )

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # ========================================================
    # Base de données — Supabase (PostgreSQL)
    # ========================================================
    # DATABASE_URL = chaîne de connexion PostgreSQL (Supabase > Connect >
    # "Transaction pooler", port 6543). Ce n'est PAS l'URL https://xxx.supabase.co.
    # Sans DATABASE_URL, retombe sur SQLite local (développement uniquement).

    SQLALCHEMY_DATABASE_URI = (
        _normalize_db_url(os.environ.get('DATABASE_URL'))
        or 'sqlite:///' + os.path.join(BASE_DIR, 'pdsc_dev.sqlite3')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = (
        _engine_options()
        if SQLALCHEMY_DATABASE_URI.startswith('postgresql')
        else {}
    )

    # ========================================================
    # Supabase Storage (fichiers uploadés)
    # ========================================================
    # SUPABASE_KEY doit être la clé "service_role" (côté serveur uniquement,
    # jamais exposée au navigateur).

    SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

    # Bucket PUBLIC : avatars, services, actualités, galerie, documents publics,
    # plans d'urbanisme, QR codes.
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'pdsc-public')

    # Bucket PRIVÉ : pièces jointes des demandes des citoyens
    # (servies via une URL signée après contrôle d'accès).
    SUPABASE_PRIVATE_BUCKET = os.environ.get(
        'SUPABASE_PRIVATE_BUCKET', 'pdsc-private'
    )

    # ========================================================
    # Internationalisation
    # ========================================================

    LANGUAGES = ['fr', 'ar']

    BABEL_DEFAULT_LOCALE = 'fr'

    BABEL_DEFAULT_TIMEZONE = 'Africa/Casablanca'

    BABEL_TRANSLATION_DIRECTORIES = os.path.join(
        BASE_DIR,
        'translations'
    )

    # ========================================================
    # Upload de fichiers
    # ========================================================

    # Utilisé uniquement en développement local (sans Supabase Storage).
    # Sur Vercel le disque est en lecture seule : Supabase Storage est obligatoire.
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        'static',
        'uploads'
    )

    # Vercel limite le corps d'une requête à 4,5 Mo : on reste en dessous.
    MAX_CONTENT_LENGTH = (4 if IS_VERCEL else 10) * 1024 * 1024

    ALLOWED_DOCUMENT_EXTENSIONS = {
        'pdf',
        'doc',
        'docx',
        'jpg',
        'jpeg',
        'png'
    }

    ALLOWED_IMAGE_EXTENSIONS = {
        'jpg',
        'jpeg',
        'png',
        'gif',
        'webp'
    }

    # ========================================================
    # Flask-Mail
    # ========================================================

    MAIL_SERVER = os.environ.get(
        'MAIL_SERVER',
        'smtp.gmail.com'
    )

    MAIL_PORT = int(
        os.environ.get('MAIL_PORT', 587)
    )

    MAIL_USE_TLS = (
        os.environ.get(
            'MAIL_USE_TLS',
            'true'
        ).lower() == 'true'
    )

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')

    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        'contact@commune.ma'
    )

    # ========================================================
    # JWT
    # ========================================================

    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY',
        'change-this-jwt-secret-in-production'
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    JWT_TOKEN_LOCATION = ['headers']

    # ========================================================
    # Application
    # ========================================================

    ITEMS_PER_PAGE = 10

    COMMUNE_NAME_FR = os.environ.get(
        'COMMUNE_NAME_FR',
        'Commune de Zinat'
    )

    COMMUNE_NAME_AR = os.environ.get(
        'COMMUNE_NAME_AR',
        'جماعة زينات'
    )

    SECURITY_PASSWORD_SALT = os.environ.get(
        'SECURITY_PASSWORD_SALT',
        'change-this-salt'
    )


# ============================================================
# Développement
# ============================================================

class DevelopmentConfig(Config):

    DEBUG = True

    SQLALCHEMY_ECHO = False


# ============================================================
# Production - Vercel
# ============================================================

class ProductionConfig(Config):

    DEBUG = False

    SESSION_COOKIE_SECURE = True

    REMEMBER_COOKIE_SECURE = True

    SESSION_COOKIE_HTTPONLY = True


# ============================================================
# Tests
# ============================================================

class TestingConfig(Config):

    TESTING = True

    WTF_CSRF_ENABLED = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )

    SQLALCHEMY_ENGINE_OPTIONS = {}


# ============================================================
# Configuration selon l'environnement
# ============================================================

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig,
}


def get_config():
    """
    Retourne la configuration correspondant à l'environnement.
    Production est utilisée par défaut pour Vercel.
    """

    env = os.environ.get(
        'FLASK_ENV',
        'production'
    )

    return config_by_name.get(
        env,
        ProductionConfig
    )