#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Producer de Kafka que simula el seguimiento de equipaje en un aeropuerto.
Genera eventos aleatorios como equipaje_escaneado, equipaje_cargado, equipaje_entregado.
"""

import json
import uuid
import time
import random
import logging
from datetime import datetime
from kafka import KafkaProducer

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('producer')

# Configuración de Kafka
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'eventos_equipaje'

# Tipos de eventos
TIPOS_EVENTOS = [
    'equipaje_escaneado',
    'equipaje_cargado',
    'equipaje_entregado'
]

# Aeropuertos para orígenes y destinos
AEROPUERTOS = [
    'EZE', 'AEP', 'COR', 'MDZ', 'BRC',  # Argentina
    'GRU', 'SCL', 'LIM', 'BOG', 'MEX',  # América Latina
    'MIA', 'JFK', 'LAX', 'DFW', 'ORD',  # Estados Unidos
    'MAD', 'BCN', 'CDG', 'LHR', 'FRA'   # Europa
]

def conectar_kafka():
    """
    Establece conexión con el broker de Kafka.
    
    Returns:
        KafkaProducer: Instancia del producer de Kafka o None si falla la conexión.
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        logger.info(f"Conectado al broker Kafka: {KAFKA_BROKER}")
        return producer
    except Exception as e:
        logger.error(f"Error al conectar con Kafka: {e}")
        return None

def generar_id_valija():
    """
    Genera un ID único para una valija.
    
    Returns:
        str: ID único para la valija.
    """
    return str(uuid.uuid4())

def generar_evento_aleatorio(id_valija=None):
    """
    Genera un evento aleatorio de equipaje.
    
    Args:
        id_valija (str, optional): ID de la valija. Si es None, se genera uno nuevo.
    
    Returns:
        tuple: id_valija, datos del evento
    """
    # Si no se proporciona un ID de valija, generar uno nuevo
    if id_valija is None:
        id_valija = generar_id_valija()
    
    # Seleccionar tipo de evento aleatorio
    tipo_evento = random.choice(TIPOS_EVENTOS)
    
    # Generar origen y destino para el equipaje
    origen = random.choice(AEROPUERTOS)
    destino = random.choice([a for a in AEROPUERTOS if a != origen])
    
    # Generar peso aleatorio para el equipaje (entre 5 y 32 kg)
    peso = round(random.uniform(5.0, 32.0), 1)
    
    # Crear el evento
    evento = {
        'evento': tipo_evento,
        'id_valija': id_valija,
        'timestamp': datetime.now().isoformat(),
        'origen': origen,
        'destino': destino,
        'peso': peso
    }
    
    return id_valija, evento

def enviar_evento(producer, evento):
    """
    Envía un evento al topic de Kafka.
    
    Args:
        producer (KafkaProducer): Producer de Kafka.
        evento (dict): Datos del evento a enviar.
    
    Returns:
        bool: True si el envío fue exitoso, False en caso contrario.
    """
    try:
        # Enviar evento a Kafka
        future = producer.send(TOPIC_NAME, value=evento)
        producer.flush()  # Asegurar que el mensaje se envíe inmediatamente
        future.get(timeout=10)  # Esperar confirmación
        logger.info(f"Evento enviado: {evento['evento']} - Valija: {evento['id_valija']}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar evento a Kafka: {e}")
        return False

def simular_flujo_equipaje():
    """
    Simula el flujo de equipaje generando eventos para el mismo ID de valija
    en una secuencia lógica.
    """
    id_valija = generar_id_valija()
    
    # Simular el flujo completo de una valija
    eventos_secuencia = [
        'equipaje_escaneado',
        'equipaje_cargado',
        'equipaje_entregado'
    ]
    
    # Datos comunes para todos los eventos de esta valija
    origen = random.choice(AEROPUERTOS)
    destino = random.choice([a for a in AEROPUERTOS if a != origen])
    peso = round(random.uniform(5.0, 32.0), 1)
    
    for tipo_evento in eventos_secuencia:
        evento = {
            'evento': tipo_evento,
            'id_valija': id_valija,
            'timestamp': datetime.now().isoformat(),
            'origen': origen,
            'destino': destino,
            'peso': peso
        }
        
        yield id_valija, evento

def main():
    """
    Función principal que ejecuta el productor de eventos.
    """
    producer = conectar_kafka()
    if not producer:
        logger.error("No se pudo conectar a Kafka. Saliendo...")
        return
    
    try:
        valijas_en_proceso = {}  # Para mantener registro de valijas en proceso
        
        logger.info("Iniciando simulación de eventos de equipaje...")
        
        while True:
            # Decidir si generar un evento completamente nuevo o continuar con una valija existente
            if valijas_en_proceso and random.random() < 0.7:  # 70% probabilidad de continuar con valija existente
                # Seleccionar una valija existente y generar el siguiente evento en su flujo
                id_valija = random.choice(list(valijas_en_proceso.keys()))
                estado_actual = valijas_en_proceso[id_valija]
                
                # Definir el próximo estado basado en el estado actual
                if estado_actual == 'equipaje_escaneado':
                    siguiente_estado = 'equipaje_cargado'
                elif estado_actual == 'equipaje_cargado':
                    siguiente_estado = 'equipaje_entregado'
                else:
                    # Si ya está entregado, eliminar de las valijas en proceso y generar una nueva
                    del valijas_en_proceso[id_valija]
                    id_valija, evento = generar_evento_aleatorio()
                    siguiente_estado = evento['evento']
                
                if id_valija in valijas_en_proceso:
                    # Crear el evento para la siguiente etapa
                    evento = {
                        'evento': siguiente_estado,
                        'id_valija': id_valija,
                        'timestamp': datetime.now().isoformat(),
                        'origen': random.choice(AEROPUERTOS),
                        'destino': random.choice(AEROPUERTOS),
                        'peso': round(random.uniform(5.0, 32.0), 1)
                    }
                    
                    # Actualizar el estado de la valija
                    valijas_en_proceso[id_valija] = siguiente_estado
                    
                    # Si la valija ha completado su ciclo, eliminarla
                    if siguiente_estado == 'equipaje_entregado':
                        del valijas_en_proceso[id_valija]
            else:
                # Generar un nuevo evento para una valija nueva
                id_valija, evento = generar_evento_aleatorio()
                valijas_en_proceso[id_valija] = evento['evento']
            
            # Enviar el evento a Kafka
            if enviar_evento(producer, evento):
                # Información adicional para debugging
                logger.debug(f"Estado actual de valijas en proceso: {valijas_en_proceso}")
            
            # Esperar un tiempo aleatorio entre 2 y 5 segundos
            time.sleep(random.uniform(2, 5))
            
    except KeyboardInterrupt:
        logger.info("Deteniendo el productor de eventos...")
    finally:
        if producer:
            producer.close()
            logger.info("Productor cerrado correctamente")

if __name__ == "__main__":
    main()