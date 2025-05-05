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
# Corregir la ruta base para apuntar al directorio principal del proyecto, no al directorio utils
utils_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(utils_dir)  # Subir un nivel para obtener el directorio raíz del proyecto
print(f"Directorio utils: {utils_dir}")
print(f"Directorio base: {base_dir}")

# Verificar directorios principales
dirs_to_check = [
    'src', 'src/api', 'src/core', 'src/simulador',
    'static', 'templates', 'data', 'config', 'utils'
]

for dir_path in dirs_to_check:
    full_path = os.path.join(base_dir, dir_path)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        print(f"✅ Directorio {dir_path}: Existe")
    else:
        print(f"❌ Directorio {dir_path}: No existe")
        # Crear directorios faltantes si es posible
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"  ✓ Directorio {dir_path} creado.")
        except Exception as e:
            print(f"  ✗ No se pudo crear el directorio: {e}")

# Verificar archivos principales
files_to_check = [
    'app.py', 'wsgi.py', 'requirements.txt', 'README.md',
    'src/api/routes.py', 'src/core/config.py', 'src/core/db_service.py',
    'src/simulador/simulador_auto.py'
]

for file_path in files_to_check:
    full_path = os.path.join(base_dir, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        print(f"✅ Archivo {file_path}: Existe ({os.path.getsize(full_path)} bytes)")
    else:
        print(f"❌ Archivo {file_path}: No existe")

# Verificar la base de datos
db_path = os.path.join(base_dir, 'data', 'equipajes.db')
if os.path.exists(db_path) and os.path.isfile(db_path):
    print(f"✅ Base de datos: Existe ({os.path.getsize(db_path)} bytes)")
else:
    print(f"❌ Base de datos: No existe en {db_path}")
    # Verificar si la base de datos está en la raíz del proyecto
    root_db_path = os.path.join(base_dir, 'equipajes.db')
    if os.path.exists(root_db_path) and os.path.isfile(root_db_path):
        print(f"  ✓ Base de datos encontrada en la raíz: {root_db_path}")
        # Intentar mover a la ubicación correcta
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            import shutil
            shutil.copy2(root_db_path, db_path)
            print(f"  ✓ Base de datos copiada de la raíz a {db_path}")
        except Exception as e:
            print(f"  ✗ Error al copiar la base de datos: {e}")

# Agregar la raíz del proyecto a sys.path para importaciones
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
    print("\nAgregado al path:", base_dir)

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
        # Intentar instalar el paquete
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
            print(f"  ✓ {package} instalado automáticamente.")
        except Exception as e:
            print(f"  ✗ No se pudo instalar {package}: {e}")

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
if os.path.exists(db_path):
    # Verificar permisos de lectura
    readable = os.access(db_path, os.R_OK)
    writable = os.access(db_path, os.W_OK)
    print(f"Base de datos {db_path}:")
    print(f"  - Permiso de lectura: {'✅ Sí' if readable else '❌ No'}")
    print(f"  - Permiso de escritura: {'✅ Sí' if writable else '❌ No'}")
    
    # Intentar arreglar permisos si es necesario
    if not (readable and writable):
        try:
            os.chmod(db_path, 0o664)
            print("  ✓ Permisos de base de datos ajustados a 664")
        except Exception as e:
            print(f"  ✗ No se pudieron ajustar permisos: {e}")
    
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
                # Intentar actualizar el archivo WSGI
                try:
                    with open(wsgi_path, 'w', encoding='utf-8') as f:
                        f.write(local_content)
                    print("  ✓ Archivo WSGI actualizado con contenido local")
                except Exception as e:
                    print(f"  ✗ No se pudo actualizar el archivo WSGI: {e}")
        except Exception as e:
            print(f"❌ Error al leer archivo WSGI en PythonAnywhere: {e}")
else:
    print(f"❌ Archivo WSGI local: No existe")

# Crear archivo __init__.py en cada carpeta de src para solucionar problemas de importación
print("\n8. CONFIGURACIÓN DE PAQUETES PYTHON:")
init_dirs = ['src', 'src/api', 'src/core', 'src/simulador']
for dir_path in init_dirs:
    full_dir = os.path.join(base_dir, dir_path)
    init_file = os.path.join(full_dir, '__init__.py')
    
    if not os.path.exists(full_dir):
        print(f"❌ No se puede crear __init__.py en {dir_path} - El directorio no existe")
        continue
        
    if not os.path.exists(init_file):
        try:
            with open(init_file, 'w') as f:
                f.write("# Archivo de inicialización para el paquete\n")
            print(f"✅ Creado __init__.py en {dir_path}")
        except Exception as e:
            print(f"❌ No se pudo crear __init__.py en {dir_path}: {e}")
    else:
        print(f"✅ Ya existe __init__.py en {dir_path}")

# Resumen y recomendaciones
print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO - RECOMENDACIONES")
print("=" * 80)
print("\nESTADO DE LA APLICACIÓN:")

# Determinar el estado general
missing_dirs = any(not os.path.exists(os.path.join(base_dir, d)) for d in ['src', 'static', 'templates'])
missing_files = any(not os.path.exists(os.path.join(base_dir, f)) for f in ['app.py', 'wsgi.py'])
import_errors = False  # Se actualiza basado en las pruebas anteriores

print(f"Estructura de carpetas: {'❌ Incompleta' if missing_dirs else '✅ Completa'}")
print(f"Archivos principales: {'❌ Faltan archivos' if missing_files else '✅ Completos'}")
print(f"Importaciones: {'❌ Con errores' if import_errors else '✅ Correctas'}")
print(f"Base de datos: {'❌ No disponible' if not os.path.exists(db_path) else '✅ Disponible'}")

print("\nACCIONES RECOMENDADAS:")

if missing_dirs or missing_files:
    print("\n1. TRANSFERIR ARCHIVOS CORRECTAMENTE:")
    print("   Es necesario subir todos los archivos a PythonAnywhere conservando la estructura de carpetas.")
    print("   Métodos recomendados:")
    print("   - Usar un archivo ZIP: Comprimir todo el proyecto y subir el ZIP")
    print("   - Usar Git: Clonar el repositorio en PythonAnywhere")
    print("   - Usar SFTP: Transferir archivos manteniendo la estructura")
    print("\n   Comando para comprimir el proyecto (desde terminal local):")
    print("   zip -r ArqApp-03.zip ArqApp-03/")
    print("\n   Luego subir el ZIP a PythonAnywhere y descomprimirlo:")
    print("   unzip ArqApp-03.zip")

if not os.path.exists(db_path) and os.path.exists(os.path.join(base_dir, 'equipajes.db')):
    print("\n2. MOVER LA BASE DE DATOS:")
    print(f"   mkdir -p {os.path.dirname(db_path)}")
    print(f"   cp {os.path.join(base_dir, 'equipajes.db')} {db_path}")

print("\n3. ASEGURAR QUE EL ARCHIVO WSGI ES CORRECTO:")
print("   cp wsgi.py /var/www/fedeegea_pythonanywhere_com_wsgi.py")

print("\n4. AJUSTAR PERMISOS:")
print("   chmod -R 755 src static templates utils")
print("   chmod 664 data/equipajes.db")

print("\n5. REINICIAR LA APLICACIÓN:")
print("   Desde el panel de control: Botón 'Reload'")
print("   O ejecutar: touch /var/www/fedeegea_pythonanywhere_com_wsgi.py")

print("\n6. VERIFICAR LOGS PARA DIAGNÓSTICO FINAL:")
print("   tail -f /var/log/fedeegea.pythonanywhere.com.error.log")

print("=" * 80)