"""
Módulo de configuración central para el Sistema de Gestión de Equipajes.
Contiene todas las configuraciones y constantes utilizadas en el sistema.
"""

import os
import pytz
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('config')

# Configuración de entorno
class Config:
    """Clase que contiene toda la configuración del sistema"""
    
    # Detectar entorno
    ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/var/www')
    
    # Zona horaria
    ZONA_HORARIA = pytz.timezone('America/Argentina/Buenos_Aires')
    
    # Configuración de base de datos
    if ON_PYTHONANYWHERE:
        BASE_DIR = '/home/fedeegea/ArqApp-03'
        DB_PATH = os.path.join(BASE_DIR, 'equipajes.db')
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, 'equipajes.db')
    
    # Configuración del simulador
    INTERVALO_GENERACION = 30  # Generar nuevo evento cada X segundos
    MAX_VALIJAS_ACTIVAS = 10   # Máximo de valijas activas simultáneamente
    
    # Lista de aeropuertos disponibles
    AEROPUERTOS = [
        'EZE - Buenos Aires', 'AEP - Buenos Aires', 'COR - Córdoba', 
        'MDZ - Mendoza', 'BRC - Bariloche', 'USH - Ushuaia',
        'MAD - Madrid', 'BCN - Barcelona', 'MIA - Miami', 'JFK - Nueva York'
    ]
    
    # Configuración de la aplicación Flask
    DEBUG = not ON_PYTHONANYWHERE
    HOST = '0.0.0.0'
    PORT = 5000

# Funciones de utilidad
def get_datetime_argentina():
    """Retorna el datetime actual en la zona horaria de Argentina"""
    return datetime.now(Config.ZONA_HORARIA)

# Registrar información sobre la configuración
if Config.ON_PYTHONANYWHERE:
    logger.info(f"Ejecutando en PythonAnywhere. DB_PATH: {Config.DB_PATH}")
else:
    logger.info(f"Ejecutando en entorno de desarrollo local. DB_PATH: {Config.DB_PATH}")

logger.info(f"Zona horaria configurada: {Config.ZONA_HORARIA}")