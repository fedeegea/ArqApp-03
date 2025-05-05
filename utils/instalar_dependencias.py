#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para instalar las dependencias necesarias en PythonAnywhere.
Ejecutar desde la consola de PythonAnywhere con:
python utils/instalar_dependencias.py
"""

import sys
import os
import subprocess
import time

print("=" * 80)
print("INSTALACIÓN DE DEPENDENCIAS PARA SISTEMA DE GESTIÓN DE EQUIPAJES")
print("=" * 80)

# Verificar que estamos en un entorno virtual
in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if not in_virtualenv:
    print("⚠️ ADVERTENCIA: No estás en un entorno virtual. Se recomienda activarlo:")
    print("   source venv/bin/activate")
    respuesta = input("¿Deseas continuar de todos modos? (s/n): ").lower()
    if respuesta != 's' and respuesta != 'si':
        print("Instalación cancelada. Activa el entorno virtual e intenta de nuevo.")
        sys.exit(1)
else:
    print("✅ Ejecutando en entorno virtual:", sys.prefix)

# Lista de dependencias a instalar
dependencias = [
    'flask',
    'pytz',
    'pandas',
    'sqlite3',
    'numpy',
    'markdown',
    'gunicorn'
]

# Instalar cada dependencia
print("\nInstalando dependencias:")
for dep in dependencias:
    print(f"Instalando {dep}...")
    try:
        # Usar subprocess para ejecutar pip install
        proceso = subprocess.run(
            [sys.executable, "-m", "pip", "install", dep],
            capture_output=True,
            text=True
        )
        
        # Verificar si la instalación fue exitosa
        if proceso.returncode == 0:
            print(f"✅ {dep} instalado correctamente")
        else:
            print(f"❌ Error al instalar {dep}: {proceso.stderr}")
            
            # Si falla con sqlite3, es porque viene integrado con Python
            if dep == 'sqlite3' and 'not find a version that satisfies the requirement' in proceso.stderr:
                print("   SQLite3 ya viene integrado con Python, no es necesario instalarlo")
    except Exception as e:
        print(f"❌ Error inesperado al instalar {dep}: {str(e)}")
    
    # Breve pausa para no sobrecargar el servidor
    time.sleep(0.5)

# Instalar desde requirements.txt si existe
req_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'requirements.txt')
if os.path.exists(req_path):
    print("\nInstalando dependencias desde requirements.txt...")
    try:
        proceso = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req_path],
            capture_output=True,
            text=True
        )
        if proceso.returncode == 0:
            print("✅ Dependencias de requirements.txt instaladas correctamente")
        else:
            print(f"❌ Error al instalar desde requirements.txt: {proceso.stderr}")
    except Exception as e:
        print(f"❌ Error inesperado al instalar desde requirements.txt: {str(e)}")

# Verificar que Flask está instalado
try:
    import flask
    print(f"\n✅ Flask instalado correctamente (versión {flask.__version__})")
except ImportError:
    print("\n❌ No se pudo importar Flask. La instalación podría haber fallado.")
    print("   Intenta ejecutar manualmente: pip install flask")

print("\n" + "=" * 80)
print("FINALIZADO - PASOS ADICIONALES")
print("=" * 80)
print("\n1. Recarga tu aplicación en PythonAnywhere:")
print("   - Ve al dashboard de PythonAnywhere")
print("   - Haz clic en el botón 'Reload' en la sección Web")
print("\n2. Si sigues teniendo problemas, actualiza el archivo WSGI:")
print("   cp wsgi.py /var/www/fedeegea_pythonanywhere_com_wsgi.py")
print("\n3. Verifica los logs de error después de recargar:")
print("   tail -n 50 /var/log/fedeegea.pythonanywhere.com.error.log")
print("=" * 80)