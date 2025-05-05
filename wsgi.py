"""
Archivo WSGI para PythonAnywhere - Sistema de Gestión de Equipajes (Versión simplificada)
"""

import sys
import os

# Agregar directorio raíz al path
path = '/home/fedeegea/ArqApp-03'
if path not in sys.path:
    sys.path.insert(0, path)

# Intentar activar el entorno virtual
try:
    activate_this = os.path.join(path, 'venv/bin/activate_this.py')
    if os.path.exists(activate_this):
        with open(activate_this) as file_:
            exec(file_.read(), dict(__file__=activate_this))
except Exception:
    pass  # Continuar aunque falle la activación

# Configurar simulador automático
os.environ['START_SIMULATOR'] = 'True'

# Importar la aplicación Flask
from app import app as application