"""
Este archivo configura la aplicación Flask para PythonAnywhere
"""

import sys
import os

# Agrega el directorio del proyecto al path de Python
path = '/home/fedeegea/ArqApp-03'
if path not in sys.path:
    sys.path.insert(0, path)

# Importa la aplicación Flask desde app.py
from app import app as application

# Asegúrate que la aplicación no se ejecuta en modo debug en producción
application.config['DEBUG'] = False

# Variables de entorno adicionales si son necesarias
os.environ['FLASK_ENV'] = 'production'