"""
Módulo para manejar las interacciones con la base de datos del sistema de gestión de equipajes.
Este módulo proporciona funciones para realizar operaciones CRUD en la base de datos.
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta
import pytz

# Importar la configuración centralizada
from src.core.config import Config

logger = logging.getLogger('db-service')

# Configuración de zona horaria para Argentina (Buenos Aires)
ZONA_HORARIA = pytz.timezone('America/Argentina/Buenos_Aires')

# Función para obtener datetime actual en zona horaria Argentina
def get_datetime_argentina():
    """Retorna el datetime actual en la zona horaria de Argentina"""
    return datetime.now(ZONA_HORARIA)

# Usar la configuración centralizada para la ruta de la base de datos
DB_PATH = Config.DB_PATH
logger.info(f"Base de datos configurada en: {DB_PATH}")

def get_db_connection():
    """
    Establece una conexión con la base de datos SQLite.
    
    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    # Verificar si el directorio existe
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Creado directorio para la base de datos: {db_dir}")
    
    # Conectar a la base de datos única en data/equipajes.db
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para obtener los resultados como diccionarios
        return conn
    except Exception as e:
        logger.error(f"Error crítico al conectar a la base de datos {DB_PATH}: {e}")
        raise

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
    Garantiza que los campos requeridos nunca sean None para evitar errores en el frontend.
    
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
        # Convertir los objetos Row a diccionarios y limpiar valores None
        valijas_list = []
        for valija in valijas:
            v = dict(valija)
            v['id_valija'] = v.get('id_valija') or ''
            v['ultimo_evento'] = v.get('ultimo_evento') or ''
            v['estado'] = v.get('estado') or 'desconocido'
            v['origen'] = v.get('origen') or 'No especificado'
            v['destino'] = v.get('destino') or 'No especificado'
            valijas_list.append(v)
        return valijas_list
    except Exception as e:
        logger.error(f"Error al obtener lista de valijas: {e}")
        return []

def obtener_estadisticas():
    """
    Obtiene estadísticas generales de los eventos de equipaje.
    
    Returns:
        dict: Diccionario con las estadísticas.
    """
    # Valores por defecto en caso de error
    resultado = {
        'por_tipo': [],
        'ultimas_24h': 0,
        'valijas_unicas': 0
    }
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Contar eventos por tipo
        eventos_por_tipo = conn.execute(
            'SELECT evento, COUNT(*) as cantidad FROM eventos_equipaje GROUP BY evento'
        ).fetchall()
        
        # Obtener el total de valijas únicas
        valijas_unicas = conn.execute(
            'SELECT COUNT(DISTINCT id_valija) as cantidad FROM eventos_equipaje'
        ).fetchone()
        
        # Convertir a formato adecuado para JSON
        tipos = [dict(evento) for evento in eventos_por_tipo]
        resultado['por_tipo'] = tipos
        resultado['valijas_unicas'] = valijas_unicas['cantidad'] if valijas_unicas else 0
        
        # Contar eventos de las últimas 24 horas
        try:
            # Usamos el datetime actual y restamos 24 horas
            dt_actual = get_datetime_argentina()
            dt_limite = dt_actual - timedelta(hours=24)
            fecha_limite = dt_limite.isoformat()
            
            eventos_recientes = conn.execute(
                'SELECT COUNT(*) as cantidad FROM eventos_equipaje WHERE timestamp > ?',
                (fecha_limite,)
            ).fetchone()
            
            resultado['ultimas_24h'] = eventos_recientes['cantidad'] if eventos_recientes else 0
        except Exception as fecha_error:
            logger.error(f"Error al calcular fecha límite: {fecha_error}")
            # Si hay un error con la fecha, mantenemos el valor por defecto
            resultado['ultimas_24h'] = 0
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        # Ya tenemos los valores por defecto en resultado
    
    finally:
        # Cerrar la conexión solo si se abrió correctamente
        if conn:
            try:
                conn.close()
            except Exception as close_error:
                logger.error(f"Error al cerrar la conexión: {close_error}")
    
    return resultado

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