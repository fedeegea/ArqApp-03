"""
Módulo para manejar las interacciones con la base de datos del sistema de gestión de equipajes.
Este módulo proporciona funciones para realizar operaciones CRUD en la base de datos.
"""

import sqlite3
import os
import logging
from datetime import datetime
import pytz

logger = logging.getLogger('db-service')

# Configuración de zona horaria para Argentina (Buenos Aires)
ZONA_HORARIA = pytz.timezone('America/Argentina/Buenos_Aires')

# Función para obtener datetime actual en zona horaria Argentina
def get_datetime_argentina():
    """Retorna el datetime actual en la zona horaria de Argentina"""
    return datetime.now(ZONA_HORARIA)

# Detectar si estamos en PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/var/www')

# Configuración de la base de datos
if ON_PYTHONANYWHERE:
    base_dir = '/home/fedeegea/ArqApp-03'
    DB_PATH = os.path.join(base_dir, 'equipajes.db')
    logger.info(f"Ejecutando en PythonAnywhere. DB_PATH: {DB_PATH}")
else:
    DB_PATH = 'equipajes.db'

def get_db_connection():
    """
    Establece una conexión con la base de datos SQLite.
    
    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
    return conn

def inicializar_db():
    """
    Inicializa la base de datos si no existe.
    Crea la tabla de eventos_equipaje.
    
    Returns:
        bool: True si se creó la base de datos, False si ya existía o hubo un error.
    """
    try:
        if not os.path.exists(DB_PATH):
            logger.info(f"Creando base de datos {DB_PATH}")
            conn = get_db_connection()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS eventos_equipaje (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_valija TEXT NOT NULL,
                    evento TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    origen TEXT,
                    destino TEXT,
                    peso REAL
                );
            ''')
            conn.commit()
            conn.close()
            logger.info("Base de datos creada correctamente")
            return True
        return False
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        return False

def insertar_evento(id_valija, evento, origen, destino, peso, timestamp=None):
    """
    Inserta un evento de equipaje en la base de datos.
    
    Args:
        id_valija (str): ID único de la valija.
        evento (str): Tipo de evento ('equipaje_escaneado', 'equipaje_cargado', 'equipaje_entregado').
        origen (str): Lugar de origen del equipaje.
        destino (str): Lugar de destino del equipaje.
        peso (float): Peso del equipaje en kg.
        timestamp (str, optional): Marca de tiempo en formato ISO. Si es None, se utiliza la hora actual.
        
    Returns:
        bool: True si se insertó correctamente, False en caso contrario.
    """
    if timestamp is None:
        timestamp = get_datetime_argentina().isoformat()
        
    try:
        conn = get_db_connection()
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

def obtener_eventos(limit=100):
    """
    Obtiene los eventos más recientes de la base de datos.
    
    Args:
        limit (int, optional): Número máximo de eventos a obtener. Por defecto 100.
        
    Returns:
        list: Lista de eventos ordenados por timestamp descendente.
    """
    try:
        conn = get_db_connection()
        eventos = conn.execute(
            'SELECT * FROM eventos_equipaje ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        ).fetchall()
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        return [dict(evento) for evento in eventos]
    except Exception as e:
        logger.error(f"Error al obtener eventos: {e}")
        return []

def obtener_valija(id_valija):
    """
    Obtiene todos los eventos de una valija específica.
    
    Args:
        id_valija (str): ID de la valija a consultar.
        
    Returns:
        list: Lista de eventos de la valija ordenados por timestamp.
    """
    try:
        conn = get_db_connection()
        eventos = conn.execute(
            'SELECT * FROM eventos_equipaje WHERE id_valija = ? ORDER BY timestamp',
            (id_valija,)
        ).fetchall()
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        return [dict(evento) for evento in eventos]
    except Exception as e:
        logger.error(f"Error al obtener información de valija {id_valija}: {e}")
        return []

def obtener_todas_valijas():
    """
    Obtiene la lista de todas las valijas con su estado actual.
    
    Returns:
        list: Lista de valijas con su estado actual.
    """
    try:
        conn = get_db_connection()
        valijas = conn.execute(
            '''
            SELECT id_valija, 
                   MAX(timestamp) as ultimo_evento,
                   (SELECT evento FROM eventos_equipaje e2 
                    WHERE e2.id_valija = e1.id_valija 
                    ORDER BY timestamp DESC LIMIT 1) as estado,
                   (SELECT origen FROM eventos_equipaje e2 
                    WHERE e2.id_valija = e1.id_valija 
                    ORDER BY timestamp DESC LIMIT 1) as origen,
                   (SELECT destino FROM eventos_equipaje e2 
                    WHERE e2.id_valija = e1.id_valija 
                    ORDER BY timestamp DESC LIMIT 1) as destino
            FROM eventos_equipaje e1
            GROUP BY id_valija
            ORDER BY ultimo_evento DESC
            '''
        ).fetchall()
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        return [dict(valija) for valija in valijas]
    except Exception as e:
        logger.error(f"Error al obtener lista de valijas: {e}")
        return []

def obtener_estadisticas():
    """
    Obtiene estadísticas generales de los eventos de equipaje.
    
    Returns:
        dict: Diccionario con las estadísticas.
    """
    try:
        conn = get_db_connection()
        
        # Contar eventos por tipo
        eventos_por_tipo = conn.execute(
            'SELECT evento, COUNT(*) as cantidad FROM eventos_equipaje GROUP BY evento'
        ).fetchall()
        
        # Contar eventos de las últimas 24 horas
        fecha_limite = (get_datetime_argentina() - datetime.timedelta(hours=24)).isoformat()
        eventos_recientes = conn.execute(
            'SELECT COUNT(*) as cantidad FROM eventos_equipaje WHERE timestamp > ?',
            (fecha_limite,)
        ).fetchone()
        
        # Obtener el total de valijas únicas
        valijas_unicas = conn.execute(
            'SELECT COUNT(DISTINCT id_valija) as cantidad FROM eventos_equipaje'
        ).fetchone()
        
        conn.close()
        
        # Convertir a formato adecuado para JSON
        tipos = [dict(evento) for evento in eventos_por_tipo]
        
        return {
            'por_tipo': tipos,
            'ultimas_24h': eventos_recientes['cantidad'],
            'valijas_unicas': valijas_unicas['cantidad']
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return {'error': str(e)}

def obtener_valijas_incompletas(limit=10):
    """
    Obtiene valijas que no han completado su ciclo (no tienen evento de entrega).
    
    Args:
        limit (int, optional): Número máximo de valijas a obtener. Por defecto 10.
        
    Returns:
        list: Lista de valijas incompletas.
    """
    try:
        conn = get_db_connection()
        
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
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        return [dict(valija) for valija in valijas_incompletas]
    except Exception as e:
        logger.error(f"Error al obtener valijas incompletas: {e}")
        return []