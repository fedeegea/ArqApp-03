"""
Microservicio consumidor de eventos Kafka para detección de equipajes perdidos
y generación automática de reportes.
"""

import json
import logging
import time
import csv
import os
from kafka import KafkaConsumer

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('kafka-consumer')

# Configuración de Kafka
KAFKA_BROKER = '127.0.0.1:9092'  # Forzar IPv4
KAFKA_TOPIC = 'eventos_equipaje'

# Simulación de almacenamiento de estados de equipaje
equipaje_estado = {}
TIEMPO_MAX_ESPERA = 60 * 10  # 10 minutos para demo

def procesar_evento(evento):
    equipaje_id = evento.get('equipaje_id')
    estado = evento.get('estado')
    timestamp = evento.get('timestamp')
    origen = evento.get('origen')
    destino = evento.get('destino')
    peso = evento.get('peso')
    
    if not equipaje_id or not estado:
        logger.warning('Evento inválido: %s', evento)
        return

    # Actualizar estado
    equipaje_estado[equipaje_id] = {'estado': estado, 'timestamp': timestamp}
    logger.info(f"Equipaje {equipaje_id} actualizado a estado '{estado}'")

    # Si el evento es de equipaje perdido, generar reporte automático
    if estado == 'equipaje_perdido':
        generar_reporte_perdida(equipaje_id, origen, destino, peso, timestamp)

# Nueva función para guardar reporte de equipaje perdido
def generar_reporte_perdida(equipaje_id, origen, destino, peso, timestamp):
    ruta = os.path.join(os.path.dirname(__file__), 'reportes_perdidas.csv')
    existe = os.path.isfile(ruta)
    with open(ruta, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['id_valija', 'origen', 'destino', 'peso', 'timestamp'])
        writer.writerow([equipaje_id, origen, destino, peso, timestamp])
    logger.error(f"REPORTE AUTOMÁTICO: Equipaje perdido {equipaje_id} (origen: {origen}, destino: {destino}, peso: {peso}, timestamp: {timestamp}) guardado en {ruta}")

def detectar_perdidas():
    ahora = int(time.time())
    for equipaje_id, info in equipaje_estado.items():
        if info['estado'] != 'entregado' and (ahora - info['timestamp']) > TIEMPO_MAX_ESPERA:
            logger.error(f"Equipaje perdido detectado: {equipaje_id}")
            # Aquí se podría generar un reporte automático (guardar en DB, enviar email, etc.)

if __name__ == '__main__':
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='reporte-equipajes'
    )
    logger.info('Consumidor Kafka iniciado, esperando eventos...')
    try:
        while True:
            for message in consumer:
                try:
                    evento = message.value
                    procesar_evento(evento)
                    detectar_perdidas()
                except Exception as e:
                    logger.error(f"Error procesando evento Kafka: {e} | Evento: {getattr(message, 'value', None)}")
    except KeyboardInterrupt:
        logger.info('Consumidor detenido por el usuario.')
