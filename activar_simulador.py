#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para forzar la activación del simulador automático en PythonAnywhere.
Ejecutar este script manualmente en la consola de PythonAnywhere para iniciar el simulador.
"""

import os
import logging
import simulador_auto

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('activar-simulador')

print("=" * 80)
print("ACTIVACIÓN MANUAL DEL SIMULADOR AUTOMÁTICO")
print("=" * 80)

# Forzar la variable de entorno
os.environ['START_SIMULATOR'] = 'True'
print("Variable START_SIMULATOR establecida como 'True'")

# Iniciar el simulador
print("Intentando iniciar el simulador automático...")
resultado = simulador_auto.iniciar_simulador()

if resultado:
    print("✅ Simulador automático iniciado correctamente")
    print("✅ Valijas activas:", len(simulador_auto.valijas_activas))
else:
    print("❌ Error al iniciar el simulador automático")

print("\nNota: Este script inicia el simulador en esta sesión de consola.")
print("Para mantener el simulador funcionando, esta consola debe permanecer abierta.")
print("Para una solución permanente, asegúrate de que el archivo WSGI está configurado correctamente.")
print("=" * 80)

try:
    print("\nManteniendo el script activo para que el simulador siga funcionando...")
    print("Presiona Ctrl+C para detener el simulador")
    
    # Mantener el script en ejecución para que el simulador siga funcionando
    while True:
        import time
        time.sleep(10)
        print(f"Simulador activo con {len(simulador_auto.valijas_activas)} valijas en proceso")
except KeyboardInterrupt:
    print("\nSimulador detenido por el usuario")