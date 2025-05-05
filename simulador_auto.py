"""
Módulo para simular la generación y procesamiento automático de eventos de equipaje
sin necesidad de ejecutar producer.py y consumer.py manualmente.
"""

import threading
import time
import random
import uuid
import sqlite3
import logging
from datetime import datetime, timedelta
import os

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('simulador-auto')

# Configuración
DB_PATH = 'equipajes.db'
INTERVALO_GENERACION = 15  # Generar nuevo evento cada X segundos
MAX_VALIJAS_ACTIVAS = 20  # Número máximo de valijas activas en el sistema

# Lista de aeropuertos disponibles
AEROPUERTOS = [
    'EZE - Buenos Aires', 'AEP - Buenos Aires', 'COR - Córdoba', 
    'MDZ - Mendoza', 'BRC - Bariloche', 'USH - Ushuaia',
    'MAD - Madrid', 'BCN - Barcelona', 'MIA - Miami', 'JFK - Nueva York'
]

# Estados de seguimiento de las valijas
valijas_activas = {}  # Diccionario para mantener el estado de las valijas activas

def obtener_conexion_db():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insertar_evento(id_valija, evento, origen, destino, peso, timestamp=None):
    """Inserta un evento de equipaje en la base de datos."""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
        
    try:
        conn = obtener_conexion_db()
        conn.execute(
            '''
            INSERT INTO eventos_equipaje 
            (id_valija, evento, timestamp, origen, destino, peso)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (id_valija, evento, timestamp, origen, destino, peso)
        )
        conn.commit()
        conn.close()
        logger.info(f"Evento insertado: {evento} para valija {id_valija}")
        return True
    except Exception as e:
        logger.error(f"Error al insertar evento: {e}")
        return False

def generar_nuevo_equipaje():
    """Genera un nuevo equipaje con evento inicial (escaneado)."""
    id_valija = str(uuid.uuid4())
    origen = random.choice(AEROPUERTOS)
    
    # Asegurar que destino sea diferente al origen
    destinos_posibles = [a for a in AEROPUERTOS if a != origen]
    destino = random.choice(destinos_posibles)
    
    peso = round(random.uniform(5, 30), 1)  # Peso entre 5 y 30 kg
    
    # Insertar evento de escaneado
    insertar_evento(id_valija, 'equipaje_escaneado', origen, destino, peso)
    
    # Agregar a valijas activas con tiempo estimado para próximo evento
    tiempo_proxima_accion = datetime.now() + timedelta(seconds=random.randint(30, 120))
    valijas_activas[id_valija] = {
        'id': id_valija,
        'origen': origen,
        'destino': destino,
        'peso': peso,
        'estado_actual': 'equipaje_escaneado',
        'tiempo_proxima_accion': tiempo_proxima_accion
    }
    
    return id_valija

def procesar_equipajes_activos():
    """Procesa las valijas activas y genera eventos según corresponda."""
    # Lista para almacenar valijas a eliminar
    valijas_a_eliminar = []
    
    # Verificar cada valija activa
    for id_valija, info in valijas_activas.items():
        # Si es hora de la próxima acción
        if datetime.now() >= info['tiempo_proxima_accion']:
            estado_actual = info['estado_actual']
            
            # Determinar próximo estado según el estado actual
            if estado_actual == 'equipaje_escaneado':
                # Cambiar a estado cargado
                insertar_evento(id_valija, 'equipaje_cargado', 
                               info['origen'], info['destino'], info['peso'])
                
                # Actualizar estado y programar próxima acción
                info['estado_actual'] = 'equipaje_cargado'
                info['tiempo_proxima_accion'] = datetime.now() + timedelta(
                    seconds=random.randint(60, 180))
                
            elif estado_actual == 'equipaje_cargado':
                # Cambiar a estado entregado
                insertar_evento(id_valija, 'equipaje_entregado', 
                               info['origen'], info['destino'], info['peso'])
                
                # Marcar para eliminar de valijas activas
                valijas_a_eliminar.append(id_valija)
    
    # Eliminar valijas completadas
    for id_valija in valijas_a_eliminar:
        del valijas_activas[id_valija]
        logger.info(f"Valija {id_valija} completó el ciclo y fue eliminada de activas")

def cargar_estado_inicial():
    """Carga el estado de valijas existentes en la base de datos."""
    try:
        conn = obtener_conexion_db()
        
        # Obtener valijas que no han completado su ciclo (no tienen evento de entrega)
        valijas_incompletas = conn.execute('''
            SELECT e1.id_valija, e1.evento, e1.origen, e1.destino, e1.peso, e1.timestamp
            FROM eventos_equipaje e1
            JOIN (
                SELECT id_valija, MAX(timestamp) as last_timestamp
                FROM eventos_equipaje
                GROUP BY id_valija
            ) e2 ON e1.id_valija = e2.id_valija AND e1.timestamp = e2.last_timestamp
            WHERE e1.evento != 'equipaje_entregado'
            ORDER BY e1.timestamp DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        # Agregar valijas incompletas al seguimiento
        for valija in valijas_incompletas:
            id_valija = valija['id_valija']
            
            # Verificar si ya está en las activas
            if id_valija in valijas_activas:
                continue
                
            # Agregar a valijas activas
            tiempo_proxima_accion = datetime.now() + timedelta(seconds=random.randint(30, 120))
            valijas_activas[id_valija] = {
                'id': id_valija,
                'origen': valija['origen'],
                'destino': valija['destino'],
                'peso': valija['peso'],
                'estado_actual': valija['evento'],
                'tiempo_proxima_accion': tiempo_proxima_accion
            }
            
        logger.info(f"Se cargaron {len(valijas_incompletas)} valijas incompletas para seguimiento")
    except Exception as e:
        logger.error(f"Error al cargar estado inicial: {e}")

def simulador_eventos():
    """Función principal que ejecuta el simulador de eventos."""
    logger.info("Iniciando simulador automático de eventos de equipaje")
    
    # Cargar estado inicial
    cargar_estado_inicial()
    
    # Variable para controlar cuándo generar nueva valija
    ultima_generacion = datetime.now() - timedelta(seconds=INTERVALO_GENERACION)  # Generar una al inicio
    
    try:
        while True:
            # Procesar equipajes activos existentes
            procesar_equipajes_activos()
            
            # Generar nueva valija si es tiempo y no excedemos el límite
            if (datetime.now() - ultima_generacion).total_seconds() >= INTERVALO_GENERACION and \
               len(valijas_activas) < MAX_VALIJAS_ACTIVAS:
                generar_nuevo_equipaje()
                ultima_generacion = datetime.now()
                logger.info(f"Valijas activas: {len(valijas_activas)}")
            
            # Breve pausa para no saturar la CPU
            time.sleep(5)
            
    except Exception as e:
        logger.error(f"Error en el simulador: {e}")
    finally:
        logger.info("Simulador detenido")

# Función para iniciar el simulador en un hilo separado
def iniciar_simulador():
    """Inicia el simulador en un hilo separado."""
    # Verificar si la base de datos existe
    if not os.path.exists(DB_PATH):
        logger.error(f"La base de datos {DB_PATH} no existe. No se puede iniciar el simulador.")
        return False
    
    # Crear y arrancar el hilo del simulador
    hilo_simulador = threading.Thread(target=simulador_eventos, daemon=True)
    hilo_simulador.start()
    logger.info("Hilo del simulador iniciado correctamente")
    return True

# Para pruebas independientes
if __name__ == "__main__":
    iniciar_simulador()
    try:
        # Mantener el programa principal vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulador detenido por el usuario")