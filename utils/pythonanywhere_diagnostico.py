#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para PythonAnywhere - Sistema de Gestión de Equipajes
Este script verifica la configuración del entorno y soluciona problemas comunes.
Ejecutar en la consola de PythonAnywhere.
"""

import os
import sys
import platform
import importlib.util
import subprocess
from datetime import datetime

# Banner
print("=" * 80)
print("DIAGNÓSTICO DE SISTEMA DE GESTIÓN DE EQUIPAJES EN PYTHONANYWHERE")
print("=" * 80)
print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python versión: {platform.python_version()}")
print(f"Sistema: {platform.system()} {platform.release()}")
print("=" * 80)

# Verificar estructura del proyecto
print("\n1. VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO:")
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Directorio base: {base_dir}")

# Verificar directorios principales
dirs_to_check = [
    'src', 'src/api', 'src/core', 'src/simulador',
    'static', 'templates', 'data', 'config'
]

for dir_path in dirs_to_check:
    full_path = os.path.join(base_dir, dir_path)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        print(f"✅ Directorio {dir_path}: Existe")
    else:
        print(f"❌ Directorio {dir_path}: No existe")

# Verificar archivos principales
files_to_check = [
    'app.py', 'wsgi.py', 'requirements.txt',
    'src/api/routes.py', 'src/core/config.py', 'src/core/db_service.py',
    'src/simulador/simulador_auto.py', 'data/equipajes.db'
]

for file_path in files_to_check:
    full_path = os.path.join(base_dir, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        print(f"✅ Archivo {file_path}: Existe ({os.path.getsize(full_path)} bytes)")
    else:
        print(f"❌ Archivo {file_path}: No existe")

# Verificar entorno virtual
print("\n2. VERIFICACIÓN DEL ENTORNO VIRTUAL:")
in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if in_virtualenv:
    print(f"✅ Ejecutando en entorno virtual: {sys.prefix}")
else:
    print(f"❌ No se está ejecutando en un entorno virtual")

# Verificar dependencias
print("\n3. VERIFICACIÓN DE DEPENDENCIAS:")
required_packages = ['flask', 'pytz', 'pandas']
for package in required_packages:
    spec = importlib.util.find_spec(package)
    if spec is not None:
        try:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'Desconocida')
            print(f"✅ {package}: Instalado (versión {version})")
        except (ImportError, AttributeError):
            print(f"✅ {package}: Instalado (versión desconocida)")
    else:
        print(f"❌ {package}: No instalado")

# Verificar rutas de importación
print("\n4. VERIFICACIÓN DE RUTAS DE IMPORTACIÓN:")
print(f"sys.path contiene {len(sys.path)} rutas:")
for i, path in enumerate(sys.path):
    print(f"   {i+1}. {path}")

# Probar importaciones críticas
print("\n5. PRUEBA DE IMPORTACIONES CRÍTICAS:")
imports_to_test = [
    'from src.core.config import Config',
    'from src.core.db_service import inicializar_db',
    'from src.simulador.simulador_auto import iniciar_simulador',
    'from src.api.routes import api_bp'
]

for import_stmt in imports_to_test:
    try:
        exec(import_stmt)
        print(f"✅ {import_stmt}: Éxito")
    except Exception as e:
        print(f"❌ {import_stmt}: Error - {str(e)}")

# Verificar permisos
print("\n6. VERIFICACIÓN DE PERMISOS:")
db_path = os.path.join(base_dir, 'data', 'equipajes.db')
if os.path.exists(db_path):
    # Verificar permisos de lectura
    readable = os.access(db_path, os.R_OK)
    writable = os.access(db_path, os.W_OK)
    print(f"Base de datos {db_path}:")
    print(f"  - Permiso de lectura: {'✅ Sí' if readable else '❌ No'}")
    print(f"  - Permiso de escritura: {'✅ Sí' if writable else '❌ No'}")
    print(f"  - Usuario actual: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
    print(f"  - Propietario: {os.stat(db_path).st_uid if hasattr(os.stat(db_path), 'st_uid') else 'N/A'}")
else:
    print(f"❌ Base de datos no encontrada en {db_path}")

# Verificar archivo WSGI
print("\n7. VERIFICACIÓN DEL ARCHIVO WSGI:")
wsgi_path = '/var/www/fedeegea_pythonanywhere_com_wsgi.py'
wsgi_local = os.path.join(base_dir, 'wsgi.py')

if os.path.exists(wsgi_path):
    print(f"✅ Archivo WSGI en PythonAnywhere: Existe")
else:
    print(f"❌ Archivo WSGI en PythonAnywhere: No existe o no es accesible")

if os.path.exists(wsgi_local):
    print(f"✅ Archivo WSGI local: Existe ({os.path.getsize(wsgi_local)} bytes)")
    
    # Comparar con el archivo wsgi.py local
    if os.path.exists(wsgi_path) and os.access(wsgi_path, os.R_OK):
        with open(wsgi_local, 'r', encoding='utf-8') as f1:
            local_content = f1.read()
        try:
            with open(wsgi_path, 'r', encoding='utf-8') as f2:
                pa_content = f2.read()
            if local_content == pa_content:
                print(f"✅ Contenido WSGI: Coincide con el archivo local")
            else:
                print(f"❌ Contenido WSGI: No coincide con el archivo local")
        except Exception as e:
            print(f"❌ Error al leer archivo WSGI en PythonAnywhere: {e}")
else:
    print(f"❌ Archivo WSGI local: No existe")

# Resumen y recomendaciones
print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO - RECOMENDACIONES")
print("=" * 80)
print("\nPara solucionar problemas en PythonAnywhere:")

print("\n1. Si hay problemas con la estructura del proyecto:")
print("   - Asegúrate de haber subido todos los archivos manteniendo la estructura de carpetas")
print("   - Verifica que las rutas en los imports sean correctas y usen src/...")

print("\n2. Si hay problemas con el entorno virtual:")
print("   - Activa el entorno virtual: source venv/bin/activate")
print("   - Instala dependencias: pip install -r requirements.txt")

print("\n3. Si hay problemas con el archivo WSGI:")
print("   - Copia el archivo wsgi.py actualizado a /var/www/fedeegea_pythonanywhere_com_wsgi.py")
print("   - Comando: cp wsgi.py /var/www/fedeegea_pythonanywhere_com_wsgi.py")

print("\n4. Si hay problemas de permisos:")
print("   - Ajusta permisos de la base de datos: chmod 664 data/equipajes.db")
print("   - Asegúrate que las carpetas tienen permisos adecuados: chmod -R 755 src static templates")

print("\n5. Para reiniciar la aplicación:")
print("   - Usa el botón 'Reload' en el panel de control de PythonAnywhere")
print("   - O ejecuta: touch /var/www/fedeegea_pythonanywhere_com_wsgi.py")

print("\n6. Para verificar logs:")
print("   - Revisa los logs de error desde el panel de PythonAnywhere")
print("   - O ejecuta: tail -n 100 /var/log/fedeegea.pythonanywhere.com.error.log")

print("=" * 80)