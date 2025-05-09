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
    else:
        # Subir varios niveles para llegar a la raíz del proyecto desde src/core/
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # MODIFICADO: Usar solamente la base de datos en data/equipajes.db para evitar inconsistencias
    DB_PATH = os.path.join(BASE_DIR, 'data', 'equipajes.db')
    
    # Crear directorio data si no existe
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    
    # Si existe la DB en la raíz pero no en data/, copiarla a data/ (migración)
    ROOT_DB_PATH = os.path.join(BASE_DIR, 'equipajes.db')
    if os.path.exists(ROOT_DB_PATH) and not os.path.exists(DB_PATH):
        import shutil
        try:
            shutil.copy2(ROOT_DB_PATH, DB_PATH)
            logger.info(f"Base de datos migrada de raíz a data/: {DB_PATH}")
        except Exception as e:
            logger.error(f"Error al migrar la base de datos: {e}")
    
    logger.info(f"Usando base de datos en: {DB_PATH}")
    
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