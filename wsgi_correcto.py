"""
Archivo WSGI para PythonAnywhere - Sistema de Gesti�n de Equipajes
"""

import sys
import os

# Agregar el directorio del proyecto al path
path = '/home/fedeegea/ArqApp-03'
if path not in sys.path:
    sys.path.insert(0, path)

# Activar el entorno virtual
activate_this = os.path.join(path, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Importar la aplicaci�n Flask (corregido de 'listify' a 'app')
from app import app as application

# Configurar para producci�n
application.config['DEBUG'] = False

# Para activar el simulador autom�tico (importante para el funcionamiento del simulador)
os.environ['START_SIMULATOR'] = 'True'

# Mensaje de inicializaci�n en el log
print("Aplicaci�n de Sistema de Gesti�n de Equipajes inicializada correctamente", file=sys.stderr)
