"""
Archivo WSGI para PythonAnywhere - Sistema de Gestión de Equipajes (Versión mejorada)
Este archivo debe estar ubicado en /var/www/fedeegea_pythonanywhere_com_wsgi.py
"""

import sys
import os
import traceback

# Configuración de logging más detallado
print("Iniciando configuración WSGI...", file=sys.stderr)

try:
    # Agregar el directorio del proyecto al path
    path = '/home/fedeegea/ArqApp-03'
    if path not in sys.path:
        sys.path.insert(0, path)
    print(f"Directorio del proyecto agregado al path: {path}", file=sys.stderr)

    # Verificar que el directorio existe
    if not os.path.exists(path):
        print(f"ADVERTENCIA: El directorio {path} no existe!", file=sys.stderr)
    
    # Activar el entorno virtual con manejo de errores
    try:
        activate_this = os.path.join(path, 'venv/bin/activate_this.py')
        if os.path.exists(activate_this):
            with open(activate_this) as file_:
                exec(file_.read(), dict(__file__=activate_this))
            print(f"Entorno virtual activado desde: {activate_this}", file=sys.stderr)
        else:
            print(f"ADVERTENCIA: Archivo de activación del entorno virtual no encontrado: {activate_this}", file=sys.stderr)
    except Exception as e:
        print(f"Error al activar el entorno virtual: {e}", file=sys.stderr)
        # Continuar aunque falle la activación del entorno virtual

    # Configurar la variable de entorno para el simulador automático
    os.environ['START_SIMULATOR'] = 'True'
    print("Variable START_SIMULATOR configurada como 'True'", file=sys.stderr)
    
    # Importar la aplicación Flask con manejo de errores
    try:
        from app import app as application
        print("Aplicación Flask importada correctamente", file=sys.stderr)
    except ImportError as e:
        print(f"ERROR CRÍTICO: No se pudo importar la aplicación Flask: {e}", file=sys.stderr)
        print(f"Detalles del error:\n{traceback.format_exc()}", file=sys.stderr)
        # Re-lanzar la excepción para que PythonAnywhere muestre el error
        raise

    # Configurar para producción
    application.config['DEBUG'] = False
    
    # Mensaje de inicialización en el log
    print("Aplicación de Sistema de Gestión de Equipajes inicializada correctamente", file=sys.stderr)

except Exception as e:
    print(f"ERROR CRÍTICO durante la inicialización del WSGI: {e}", file=sys.stderr)
    print(f"Detalles del error:\n{traceback.format_exc()}", file=sys.stderr)
    raise