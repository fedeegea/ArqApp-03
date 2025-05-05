#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para generar datos de prueba directamente en la base de datos
para el Sistema de Gestión de Equipajes
"""

import sqlite3
import uuid
import random
import time
from datetime import datetime, timedelta
import os.path

# Verificar si la base de datos existe
DB_PATH = 'equipajes.db'
if not os.path.exists(DB_PATH):
    print(f"Error: No se encuentra la base de datos en {DB_PATH}")
    print("Ejecuta primero setup_db.py para crear la base de datos")
    exit(1)

# Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar si ya hay datos
cursor.execute('SELECT COUNT(*) FROM eventos_equipaje')
count = cursor.fetchone()[0]
print(f"La base de datos ya contiene {count} eventos")

# Aeropuertos para origen y destino
aeropuertos = [
    'EZE - Buenos Aires', 'AEP - Buenos Aires', 'COR - Córdoba', 
    'MDZ - Mendoza', 'BRC - Bariloche', 'USH - Ushuaia',
    'MAD - Madrid', 'BCN - Barcelona', 'MIA - Miami', 'JFK - Nueva York'
]

# Función para generar un evento de equipaje
def generar_evento(id_valija=None, timestamp=None):
    if id_valija is None:
        id_valija = str(uuid.uuid4())
    
    # Si no se proporciona timestamp, usar la hora actual menos un tiempo aleatorio
    if timestamp is None:
        # Generar un timestamp en las últimas 24 horas
        tiempo_atras = random.randint(0, 24*60*60)  # segundos en 24 horas
        timestamp = (datetime.now() - timedelta(seconds=tiempo_atras)).isoformat()
    
    eventos = ['equipaje_escaneado', 'equipaje_cargado', 'equipaje_entregado']
    evento = random.choice(eventos)
    
    origen = random.choice(aeropuertos)
    destino = random.choice([a for a in aeropuertos if a != origen])
    peso = round(random.uniform(5, 30), 1)  # Peso entre 5 y 30 kg
    
    return {
        'id_valija': id_valija,
        'evento': evento,
        'timestamp': timestamp,
        'origen': origen,
        'destino': destino,
        'peso': peso
    }

# Generar nuevos eventos
def generar_nuevos_eventos(cantidad):
    # Generar IDs de valijas únicos
    ids_valijas = [str(uuid.uuid4()) for _ in range(cantidad // 3 + 1)]
    
    eventos_generados = []
    
    for id_valija in ids_valijas:
        # Para cada valija, generar una secuencia de eventos en orden correcto
        # con timestamps en orden cronológico
        
        # Hace 3-10 horas: equipaje escaneado
        horas_atras = random.randint(3, 10)
        timestamp_escaneado = (datetime.now() - timedelta(hours=horas_atras)).isoformat()
        
        evento_escaneado = generar_evento(id_valija, timestamp_escaneado)
        evento_escaneado['evento'] = 'equipaje_escaneado'
        eventos_generados.append(evento_escaneado)
        
        # 50% de probabilidad de que la valija ya haya sido cargada
        if random.random() < 0.5:
            # 1-3 horas después del escaneo
            horas_despues = random.randint(1, 3)
            timestamp_cargado = (datetime.now() - timedelta(hours=horas_atras-horas_despues)).isoformat()
            
            evento_cargado = generar_evento(id_valija, timestamp_cargado)
            evento_cargado['evento'] = 'equipaje_cargado'
            evento_cargado['origen'] = evento_escaneado['origen']
            evento_cargado['destino'] = evento_escaneado['destino']
            evento_cargado['peso'] = evento_escaneado['peso']
            eventos_generados.append(evento_cargado)
            
            # 30% de probabilidad de que la valija ya haya sido entregada
            if random.random() < 0.3:
                # 2-5 horas después de la carga
                horas_despues_entrega = random.randint(2, 5)
                timestamp_entregado = (datetime.now() - timedelta(hours=horas_atras-horas_despues-horas_despues_entrega)).isoformat()
                
                evento_entregado = generar_evento(id_valija, timestamp_entregado)
                evento_entregado['evento'] = 'equipaje_entregado'
                evento_entregado['origen'] = evento_escaneado['origen']
                evento_entregado['destino'] = evento_escaneado['destino']
                evento_entregado['peso'] = evento_escaneado['peso']
                eventos_generados.append(evento_entregado)
    
    return eventos_generados[:cantidad]  # Devolver la cantidad solicitada

# Preguntar al usuario cuántos eventos generar
cantidad_eventos = 50
print(f"Se generarán {cantidad_eventos} eventos de prueba...")

# Generar los eventos
eventos = generar_nuevos_eventos(cantidad_eventos)

# Insertar en la base de datos
for evento in eventos:
    cursor.execute(
        '''
        INSERT INTO eventos_equipaje 
        (id_valija, evento, timestamp, origen, destino, peso)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            evento['id_valija'],
            evento['evento'],
            evento['timestamp'],
            evento['origen'],
            evento['destino'],
            evento['peso']
        )
    )

# Guardar los cambios
conn.commit()

# Verificar cuántos eventos hay ahora
cursor.execute('SELECT COUNT(*) FROM eventos_equipaje')
count_final = cursor.fetchone()[0]
print(f"Datos generados correctamente. La base de datos ahora contiene {count_final} eventos")

# Mostrar algunos datos de resumen
cursor.execute('SELECT evento, COUNT(*) FROM eventos_equipaje GROUP BY evento')
stats = cursor.fetchall()
print("\nResumen por tipo de evento:")
for evento, cantidad in stats:
    print(f"  - {evento}: {cantidad} eventos")

# Mostrar las valijas con estado completo (los 3 eventos)
cursor.execute('''
    SELECT id_valija 
    FROM eventos_equipaje 
    GROUP BY id_valija 
    HAVING COUNT(DISTINCT evento) = 3
''')
valijas_completas = cursor.fetchall()
print(f"\nHay {len(valijas_completas)} valijas que han completado todo el proceso (escaneado, cargado y entregado)")

# Cerrar la conexión
conn.close()

print("\n¡Listo! Ahora puedes ver los datos en la interfaz web.")