#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para verificar la configuración del entorno en PythonAnywhere
Ejecutar en la consola de PythonAnywhere para comprobar que todo está correctamente configurado
"""

import os
import sys
import sqlite3
import datetime
import platform
import subprocess

# Banner
print("=" * 70)
print("DIAGNÓSTICO DEL SISTEMA DE GESTIÓN DE EQUIPAJES EN PYTHONANYWHERE")
print("=" * 70)

# Información del sistema
print("\n1. INFORMACIÓN DEL SISTEMA:")
print(f"   - Python: {sys.version}")
print(f"   - Plataforma: {platform.platform()}")
print(f"   - Fecha actual: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   - Directorio de trabajo: {os.getcwd()}")

# Verificar estructura de directorios
print("\n2. ESTRUCTURA DE DIRECTORIOS:")
directorio_base = os.path.dirname(os.path.abspath(__file__))
print(f"   - Directorio base: {directorio_base}")

# Comprobar directorios esenciales
directorios_esenciales = ['static', 'templates']
for directorio in directorios_esenciales:
    ruta = os.path.join(directorio_base, directorio)
    if os.path.isdir(ruta):
        print(f"   - ✅ Directorio {directorio}: Existe")
        # Mostrar algunos archivos para verificar
        archivos = os.listdir(ruta)
        if archivos:
            print(f"     - Archivos: {', '.join(archivos[:3])}{'...' if len(archivos) > 3 else ''}")
    else:
        print(f"   - ❌ Directorio {directorio}: No existe")

# Comprobar archivos esenciales
print("\n3. ARCHIVOS ESENCIALES:")
archivos_esenciales = ['app.py', 'simulador_auto.py', 'requirements.txt', 'setup_db.py']
for archivo in archivos_esenciales:
    ruta = os.path.join(directorio_base, archivo)
    if os.path.isfile(ruta):
        print(f"   - ✅ Archivo {archivo}: Existe")
        # Obtener tamaño y fecha de modificación
        tamaño = os.path.getsize(ruta)
        fecha_mod = datetime.datetime.fromtimestamp(os.path.getmtime(ruta))
        print(f"     - Tamaño: {tamaño} bytes")
        print(f"     - Modificado: {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"   - ❌ Archivo {archivo}: No existe")

# Verificar base de datos
print("\n4. BASE DE DATOS:")
db_path = os.path.join(directorio_base, 'equipajes.db')
if os.path.isfile(db_path):
    print(f"   - ✅ Base de datos: Existe en {db_path}")
    print(f"   - Tamaño: {os.path.getsize(db_path)} bytes")
    
    # Intentar abrir la base de datos y leer algunos datos
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar tabla eventos_equipaje
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos_equipaje'")
        if cursor.fetchone():
            print("   - ✅ Tabla 'eventos_equipaje': Existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) as total FROM eventos_equipaje")
            total = cursor.fetchone()[0]
            print(f"   - Total de eventos: {total}")
            
            # Mostrar algunos registros si existen
            if total > 0:
                cursor.execute("SELECT id_valija, evento, timestamp FROM eventos_equipaje ORDER BY timestamp DESC LIMIT 3")
                eventos = cursor.fetchall()
                print("   - Últimos eventos:")
                for evento in eventos:
                    print(f"     - {evento['id_valija'][:8]}... | {evento['evento']} | {evento['timestamp']}")
        else:
            print("   - ❌ Tabla 'eventos_equipaje': No existe")
            
        conn.close()
    except sqlite3.Error as e:
        print(f"   - ❌ Error al acceder a la base de datos: {e}")
else:
    print(f"   - ❌ Base de datos: No existe en {db_path}")

# Verificar módulos requeridos usando pip list en lugar de importlib
print("\n5. DEPENDENCIAS:")
try:
    with open(os.path.join(directorio_base, 'requirements.txt'), 'r') as f:
        requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    print(f"   - Total de dependencias en requirements.txt: {len(requirements)}")
    print("   - Verificando instalación:")
    
    # Ejecutar pip list para obtener los paquetes instalados
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                capture_output=True, text=True, check=True)
        import json
        installed_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(result.stdout)}
        
        for req in requirements:
            req_name = req.split('==')[0] if '==' in req else req
            if req_name.lower() in installed_packages:
                print(f"     - ✅ {req_name}: Instalado (versión {installed_packages[req_name.lower()]})")
            else:
                print(f"     - ❌ {req_name}: No instalado")
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"   - ❌ Error al obtener lista de paquetes: {e}")
        
        # Plan B: Try to import each package directly
        for req in requirements:
            req_name = req.split('==')[0] if '==' in req else req
            try:
                # Intentar importar de forma dinámica
                module = __import__(req_name.lower())
                print(f"     - ✅ {req_name}: Importado correctamente")
            except ImportError:
                print(f"     - ❌ {req_name}: Error al importar")
    
except Exception as e:
    print(f"   - ❌ Error al verificar dependencias: {e}")

# Verificar entorno virtual
print("\n6. ENTORNO VIRTUAL:")
if 'VIRTUAL_ENV' in os.environ:
    print(f"   - ✅ Entorno virtual activo: {os.environ['VIRTUAL_ENV']}")
else:
    print("   - ⚠️ No hay entorno virtual activo")
    
    # Intentar encontrar la carpeta venv
    venv_path = os.path.join(directorio_base, 'venv')
    if os.path.isdir(venv_path):
        print(f"   - ℹ️ Encontrada carpeta venv en {venv_path} (no activada)")
        print("   - Para activar, ejecuta: source venv/bin/activate")
    else:
        print("   - ℹ️ No se encontró carpeta venv")

# Verificar WSGI
print("\n7. CONFIGURACIÓN WSGI:")
wsgi_path = "/var/www/fedeegea_pythonanywhere_com_wsgi.py"
if os.path.isfile(wsgi_path):
    print(f"   - ✅ Archivo WSGI: Existe en {wsgi_path}")
    print(f"   - Tamaño: {os.path.getsize(wsgi_path)} bytes")
    print("   - Contenido (primeras líneas):")
    try:
        with open(wsgi_path, 'r') as f:
            lines = f.readlines()[:10]  # Mostrar solo las primeras 10 líneas
            for line in lines:
                print(f"     {line.rstrip()}")
    except Exception as e:
        print(f"   - ❌ Error al leer archivo WSGI: {e}")
else:
    print(f"   - ❌ Archivo WSGI: No existe en {wsgi_path}")

# Verificar importación de Flask
print("\n8. IMPORTACIÓN DE MÓDULOS PRINCIPALES:")
try:
    from flask import Flask
    import flask
    print(f"   - ✅ Flask: Importado correctamente (versión {flask.__version__})")
except ImportError:
    print("   - ❌ Flask: Error al importar")

try:
    import simulador_auto
    print("   - ✅ simulador_auto: Importado correctamente")
except ImportError:
    print("   - ❌ simulador_auto: Error al importar")

try:
    import pandas as pd
    print(f"   - ✅ pandas: Importado correctamente (versión {pd.__version__})")
except ImportError:
    print("   - ❌ pandas: Error al importar")

# Resumen
print("\n" + "=" * 70)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 70)
print("\nSi encontraste problemas, verifica:")
print("1. Que todos los archivos estén correctamente subidos a PythonAnywhere")
print("2. Que el entorno virtual esté activado y todas las dependencias instaladas")
print("3. Que el archivo WSGI apunte correctamente al directorio de la aplicación")
print("4. Que la base de datos exista y tenga la estructura correcta")
print("\nPara más información, consulta los logs de error en PythonAnywhere.")
print("=" * 70)