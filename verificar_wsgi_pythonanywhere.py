"""
Verificador para el archivo WSGI de PythonAnywhere
Este script genera el contenido correcto que debería tener el archivo WSGI en PythonAnywhere
"""

import os

# Nombre de usuario en PythonAnywhere (confirmado desde la configuración)
PYTHONANYWHERE_USERNAME = "fedeegea"

# Ruta al proyecto en PythonAnywhere (confirmada desde la configuración)
PROYECTO_PATH = f"/home/{PYTHONANYWHERE_USERNAME}/ArqApp-03"

# Contenido correcto del archivo WSGI
wsgi_content = f'''"""
Archivo WSGI para PythonAnywhere - Sistema de Gestión de Equipajes
"""

import sys
import os

# Agregar el directorio del proyecto al path
path = '{PROYECTO_PATH}'
if path not in sys.path:
    sys.path.insert(0, path)

# Activar el entorno virtual
activate_this = os.path.join(path, 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Importar la aplicación Flask (corregido de 'listify' a 'app')
from app import app as application

# Configurar para producción
application.config['DEBUG'] = False

# Para activar el simulador automático (importante para el funcionamiento del simulador)
os.environ['START_SIMULATOR'] = 'True'

# Mensaje de inicialización en el log
print("Aplicación de Sistema de Gestión de Equipajes inicializada correctamente", file=sys.stderr)
'''

# Mostrar el contenido correcto que debería tener el archivo WSGI
print("=" * 80)
print("CONTENIDO CORRECTO PARA EL ARCHIVO WSGI EN PYTHONANYWHERE")
print("=" * 80)
print(f"Ruta del archivo WSGI: /var/www/{PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py")
print("-" * 80)
print(wsgi_content)
print("-" * 80)
print(f"""
INSTRUCCIONES:
1. Accede a la consola de PythonAnywhere
2. Abre el archivo WSGI con el comando: 
   nano /var/www/{PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py

3. Borra todo el contenido actual (especialmente la línea que contiene 'from listify import app')
4. Copia y pega el contenido mostrado arriba
5. Guarda el archivo con Ctrl+O, Enter, Ctrl+X
6. Reinicia la aplicación web desde el panel "Web" de PythonAnywhere haciendo clic en el botón "Reload"
7. Comprueba los logs de error para verificar que no hay errores de importación
""")
print("=" * 80)

# Guardar el contenido en un archivo local para facilitar la transferencia
with open("wsgi_correcto.py", "w") as f:
    f.write(wsgi_content)
print(f"Se ha guardado el contenido correcto en el archivo 'wsgi_correcto.py'")
print("Puedes subir este archivo a PythonAnywhere y usar su contenido para reemplazar el archivo WSGI existente.")