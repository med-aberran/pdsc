# -*- coding: utf-8 -*-
"""
api/index.py
============
Point d'entrée serverless pour Vercel : expose l'application WSGI `app`.
Toutes les requêtes sont redirigées ici par vercel.json.
"""

import os
import sys

# Rend les modules du projet (app, models, routes...) importables.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
