#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico específico para el simulador automático en PythonAnywhere
Ejecutar en la consola de PythonAnywhere para diagnosticar problemas con el simulador
"""

import os
import sys
import sqlite3
import logging
import threading
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('diagnostico-simulador')

# Banner
print("=" * 80)
print("DIAGNÓSTICO DEL SIMULADOR AUTOMÁTICO EN PYTHONANYWHERE")
print("=" * 80)

# Verificar entorno
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/var/www')
if ON_PYTHONANYWHERE:
    print("✅ Ejecutando en PythonAnywhere")
    base_dir = '/home/fedeegea/ArqApp-03'
    DB_PATH = os.path.join(base_dir, 'equipajes.db')
else:
    print("❌ No se está ejecutando en PythonAnywhere. Este script es para diagnóstico en PythonAnywhere.")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(base_dir, 'equipajes.db')

print(f"Base del proyecto: {base_dir}")
print(f"Ruta de la base de datos: {DB_PATH}")

# Verificar archivos
print("\n1. VERIFICACIÓN DE ARCHIVOS CLAVE:")
archivos_clave = [
    'app.py', 
    'simulador_auto.py', 
    'equipajes.db'
]

for archivo in archivos_clave:
    ruta_completa = os.path.join(base_dir, archivo)
    if os.path.exists(ruta_completa):
        if os.path.isfile(ruta_completa):
            tamaño = os.path.getsize(ruta_completa)
            mod_time = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
            print(f"✅ {archivo}: Existe (Tamaño: {tamaño} bytes, Modificado: {mod_time})")
        else:
            print(f"❌ {archivo}: Existe pero no es un archivo")
    else:
        print(f"❌ {archivo}: No existe")

# Verificar base de datos
print("\n2. VERIFICACIÓN DE LA BASE DE DATOS:")
try:
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar tabla de eventos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos_equipaje'")
        if cursor.fetchone():
            print("✅ Tabla 'eventos_equipaje': Existe")
            
            # Contar eventos
            cursor.execute("SELECT COUNT(*) as total FROM eventos_equipaje")
            total = cursor.fetchone()[0]
            print(f"✅ Total de eventos en la base de datos: {total}")
            
            # Verificar permisos de escritura
            try:
                timestamp = datetime.now().isoformat()
                id_valija = f"test-{timestamp}"
                cursor.execute(
                    "INSERT INTO eventos_equipaje (id_valija, evento, timestamp, origen, destino, peso) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_valija, "test_evento", timestamp, "TEST-ORIGEN", "TEST-DESTINO", 10.0)
                )
                conn.commit()
                print("✅ Permisos de escritura en la base de datos: OK")
                
                # Eliminar el evento de prueba
                cursor.execute("DELETE FROM eventos_equipaje WHERE id_valija = ?", (id_valija,))
                conn.commit()
            except Exception as e:
                print(f"❌ Error de escritura en la base de datos: {e}")
        else:
            print("❌ Tabla 'eventos_equipaje': No existe")
        
        conn.close()
    else:
        print(f"❌ Base de datos: No encontrada en {DB_PATH}")
except Exception as e:
    print(f"❌ Error al verificar la base de datos: {e}")

# Verificar variable de entorno
print("\n3. VERIFICACIÓN DE VARIABLES DE ENTORNO:")
start_simulator = os.environ.get('START_SIMULATOR', 'No configurada')
print(f"Variable START_SIMULATOR: {start_simulator}")
if start_simulator.lower() == 'true':
    print("✅ Variable START_SIMULATOR configurada correctamente")
else:
    print("❌ Variable START_SIMULATOR no está configurada como 'True'")
    print("   Para activar el simulador, ejecuta: os.environ['START_SIMULATOR'] = 'True'")

# Verificar estado del simulador
print("\n4. VERIFICACIÓN DEL SIMULADOR:")
try:
    import simulador_auto
    print("✅ Módulo simulador_auto importado correctamente")
    
    # Verificar valijas activas
    print(f"Total de valijas activas: {len(simulador_auto.valijas_activas)}")
    
    # Información de configuración
    print(f"Intervalo de generación: {simulador_auto.INTERVALO_GENERACION} segundos")
    print(f"Máximo de valijas activas: {simulador_auto.MAX_VALIJAS_ACTIVAS}")
    
    # Probar la generación de un nuevo equipaje
    try:
        print("\nIntentando generar un nuevo equipaje de prueba...")
        id_valija = simulador_auto.generar_nuevo_equipaje()
        if id_valija:
            print(f"✅ Equipaje generado correctamente. ID: {id_valija}")
            
            # Verificar si se agregó a las valijas activas
            if id_valija in simulador_auto.valijas_activas:
                print("✅ Valija añadida correctamente a valijas_activas")
            else:
                print("❌ La valija no aparece en valijas_activas")
        else:
            print("❌ No se pudo generar un nuevo equipaje")
    except Exception as e:
        print(f"❌ Error al generar equipaje: {e}")
    
    # Probar el procesamiento de equipajes
    try:
        print("\nIntentando procesar equipajes activos...")
        simulador_auto.procesar_equipajes_activos()
        print("✅ Procesamiento de equipajes ejecutado sin errores")
    except Exception as e:
        print(f"❌ Error al procesar equipajes: {e}")
    
except ImportError:
    print("❌ No se pudo importar el módulo simulador_auto")
except Exception as e:
    print(f"❌ Error al verificar el simulador: {e}")

# Verificar los hilos en ejecución
print("\n5. VERIFICACIÓN DE HILOS:")
todos_los_hilos = threading.enumerate()
print(f"Total de hilos en ejecución: {len(todos_los_hilos)}")
for i, hilo in enumerate(todos_los_hilos):
    print(f"Hilo {i+1}: {hilo.name} ({'Daemon' if hilo.daemon else 'No daemon'})")

# Prueba de inicio manual del simulador
print("\n6. PRUEBA DE INICIO MANUAL DEL SIMULADOR:")
try:
    print("Intentando iniciar el simulador manualmente...")
    # Forzar la variable de entorno
    os.environ['START_SIMULATOR'] = 'True'
    
    # Iniciar el simulador
    resultado = simulador_auto.iniciar_simulador()
    if resultado:
        print("✅ Simulador iniciado correctamente")
        
        # Esperar un momento y verificar nuevamente los hilos
        print("Esperando 5 segundos para verificar si el hilo del simulador está en ejecución...")
        time.sleep(5)
        
        hilos_despues = threading.enumerate()
        print(f"Total de hilos después de iniciar el simulador: {len(hilos_despues)}")
        for i, hilo in enumerate(hilos_despues):
            print(f"Hilo {i+1}: {hilo.name} ({'Daemon' if hilo.daemon else 'No daemon'})")
    else:
        print("❌ No se pudo iniciar el simulador manualmente")
except Exception as e:
    print(f"❌ Error al iniciar manualmente el simulador: {e}")

# Resumen
print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)
print("\nSi detectaste problemas, estas son posibles soluciones:")
print("1. Si la base de datos no existe o no tiene la estructura correcta:")
print("   - Ejecuta python setup_db.py para crear/reiniciar la base de datos")
print("\n2. Si la variable START_SIMULATOR no está configurada como 'True':")
print("   - Edita el archivo WSGI y asegúrate de que tenga la línea: os.environ['START_SIMULATOR'] = 'True'")
print("   - O ejecuta manualmente: os.environ['START_SIMULATOR'] = 'True' y luego simulador_auto.iniciar_simulador()")
print("\n3. Si hay problemas de permisos:")
print("   - Verifica que tu usuario tenga permisos de escritura en el directorio del proyecto")
print("   - Verifica los permisos de la base de datos con: chmod 664 equipajes.db")
print("\n4. Si el simulador no genera valijas:")
print("   - Visita la URL: https://fedeegea.pythonanywhere.com/api/simulador/forzar_inicio")
print("   - Verifica el estado con: https://fedeegea.pythonanywhere.com/api/simulador/estado")
print("\n5. Reinicia la aplicación web desde el panel de control de PythonAnywhere")
print("=" * 80)