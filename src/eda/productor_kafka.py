"""
Productor de eventos Kafka para el backend Flask.
Permite publicar eventos de equipaje en el tópico de Kafka.
"""

import json
from kafka import KafkaProducer

KAFKA_BROKER = '127.0.0.1:9092'  # Forzar IPv4
KAFKA_TOPIC = 'eventos_equipaje'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publicar_evento_equipaje(evento: dict):
    """Publica un evento de equipaje en Kafka."""
    producer.send(KAFKA_TOPIC, evento)
    producer.flush()
