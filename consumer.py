#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Consumer de Kafka que lee eventos de equipaje y los almacena en la base de datos SQLite.
Procesa eventos como equipaje_escaneado, equipaje_cargado, equipaje_entregado.
"""

import json
import sqlite3
import logging
import time
from kafka import KafkaConsumer
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('consumer')

# Configuración de Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'eventos_equipaje'
GROUP_ID = 'grupo_equipaje_consumer'

# Configuración de la base de datos
DB_PATH = 'equipajes.db'

def conectar_kafka():
    """
    Establece conexión con el broker de Kafka para consumir mensajes.
    
    Returns:
        KafkaConsumer: Instancia del consumer de Kafka o None si falla la conexión.
    """
    try:
        # Intentar conectar al broker de Kafka con reintentos
        for i in range(5):  # Intentar 5 veces
            try:
                consumer = KafkaConsumer(
                    TOPIC_NAME,
                    bootstrap_servers=KAFKA_BROKER,
                    group_id=GROUP_ID,
                    auto_offset_reset='earliest',  # Comenzar desde el primer mensaje disponible
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    api_version=(0, 10, 1)
                )
                logger.info(f"Conectado al broker Kafka: {KAFKA_BROKER}")
                return consumer
            except Exception as e:
                logger.warning(f"Intento {i+1} fallido al conectar con Kafka: {e}")
                time.sleep(5)  # Esperar 5 segundos antes de reintentar
        
        raise Exception("No se pudo conectar después de múltiples intentos")
    except Exception as e:
        logger.error(f"Error al conectar con Kafka: {e}")
        return None

def conectar_db():
    """
    Establece conexión con la base de datos SQLite.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos o None si falla.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        logger.info(f"Conectado a la base de datos: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        return None

def guardar_evento(conn, evento):
    """
    Guarda un evento en la base de datos.
    
    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        evento (dict): Datos del evento a guardar.
    
    Returns:
        bool: True si el guardado fue exitoso, False en caso contrario.
    """
    try:
        cursor = conn.cursor()
        
        # Preparar la consulta SQL
        query = '''
        INSERT INTO eventos_equipaje 
        (evento, id_valija, timestamp, origen, destino, peso)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        # Ejecutar la consulta con los datos del evento
        cursor.execute(query, (
            evento['evento'],
            evento['id_valija'],
            evento['timestamp'],
            evento.get('origen', ''),  # Usar get para manejar campos opcionales
            evento.get('destino', ''),
            evento.get('peso', 0.0)
        ))
        
        conn.commit()
        logger.info(f"Evento guardado en BD: {evento['evento']} - Valija: {evento['id_valija']}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al guardar evento en base de datos: {e}")
        conn.rollback()
        return False

def procesar_eventos():
    """
    Procesa continuamente los eventos recibidos de Kafka y los almacena en la base de datos.
    """
    # Conectar al broker de Kafka
    consumer = conectar_kafka()
    if not consumer:
        logger.error("No se pudo conectar a Kafka. Saliendo...")
        return
    
    # Conectar a la base de datos
    conn = conectar_db()
    if not conn:
        logger.error("No se pudo conectar a la base de datos. Saliendo...")
        if consumer:
            consumer.close()
        return
    
    try:
        logger.info(f"Esperando eventos en el topic '{TOPIC_NAME}'...")
        
        # Iniciar el consumo de eventos
        for mensaje in consumer:
            try:
                # Obtener el evento del mensaje
                evento = mensaje.value
                
                # Imprimir información del evento recibido
                logger.info(f"Evento recibido: {evento['evento']} - Valija: {evento['id_valija']}")
                
                # Guardar el evento en la base de datos
                if not guardar_evento(conn, evento):
                    logger.warning(f"No se pudo guardar el evento: {evento}")
                
            except Exception as e:
                logger.error(f"Error al procesar mensaje: {e}")
    
    except KeyboardInterrupt:
        logger.info("Deteniendo el consumidor de eventos...")
    finally:
        # Cerrar las conexiones
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada")
        
        if consumer:
            consumer.close()
            logger.info("Consumidor de Kafka cerrado")

def main():
    """
    Función principal que ejecuta el consumidor de eventos.
    """
    logger.info("Iniciando consumidor de eventos de equipaje...")
    procesar_eventos()
    logger.info("Consumidor de eventos finalizado")

if __name__ == "__main__":
    main()