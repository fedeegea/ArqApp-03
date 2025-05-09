"""
Este módulo contiene todas las rutas API del sistema de gestión de equipajes.
Separa la lógica de las rutas de la aplicación principal siguiendo el patrón MVC.
"""

import os
import sys
from flask import Blueprint, jsonify, request
import logging

# Ajustar el path para las importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes necesarios
from src.core.config import Config, get_datetime_argentina
from src.core.db_service import (
    obtener_eventos, obtener_valija, obtener_todas_valijas, 
    insertar_evento, obtener_estadisticas
)
from src.simulador.simulador_auto import valijas_activas, iniciar_simulador
from src.eda.productor_kafka import publicar_evento_equipaje

# Configuración de logging
logger = logging.getLogger('api-routes')

# Crear Blueprint para las rutas API
api_bp = Blueprint('api', __name__)

def agregar_valija_a_simulador(id_valija, origen, destino, peso, estado_actual):
    try:
        from src.simulador.simulador_auto import valijas_activas
        from datetime import timedelta
        from src.core.config import get_datetime_argentina
        import random
        if id_valija not in valijas_activas and estado_actual in ['equipaje_escaneado', 'equipaje_cargado']:
            tiempo_proxima_accion = get_datetime_argentina() + timedelta(seconds=random.randint(30, 120))
            valijas_activas[id_valija] = {
                'id': id_valija,
                'origen': origen,
                'destino': destino,
                'peso': peso,
                'estado_actual': estado_actual,
                'tiempo_proxima_accion': tiempo_proxima_accion
            }
            logger.info(f"Valija {id_valija} añadida manualmente al simulador para cambio de estado automático")
    except Exception as e:
        logger.error(f"No se pudo agregar la valija manual al simulador: {e}")

@api_bp.route('/eventos')
def get_eventos():
    """
    API para obtener los eventos de equipaje.
    
    Returns:
        json: Lista de eventos en formato JSON.
    """
    try:
        resultado = obtener_eventos(limit=100)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener eventos: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/estadisticas')
def get_estadisticas():
    """
    API para obtener estadísticas de eventos.
    
    Returns:
        json: Estadísticas en formato JSON.
    """
    try:
        resultado = obtener_estadisticas()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/valija/<id_valija>')
def get_valija(id_valija):
    """
    API para obtener el historial de una valija específica.
    
    Args:
        id_valija (str): ID de la valija a consultar.
        
    Returns:
        json: Historial de eventos de la valija en formato JSON.
    """
    try:
        resultado = obtener_valija(id_valija)
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener información de valija {id_valija}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/valijas')
def get_valijas():
    """
    API para obtener la lista de todas las valijas.
    
    Returns:
        json: Lista de valijas en formato JSON.
    """
    try:
        resultado = obtener_todas_valijas()
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener lista de valijas: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/agregar_equipaje', methods=['POST'])
def agregar_equipaje():
    """
    API para agregar un nuevo equipaje al sistema.
    
    Returns:
        json: Resultado de la operación.
    """
    try:
        # Obtener datos del formulario
        evento = request.form.get('evento')
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        peso = request.form.get('peso')
        timestamp = request.form.get('timestamp')
        
        # Validar datos requeridos
        if not evento or not origen or not destino or not peso:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400
        
        # Generar ID de valija único
        import uuid
        id_valija = str(uuid.uuid4())
        
        # Usar timestamp proporcionado o generar uno nuevo
        if not timestamp:
            timestamp = get_datetime_argentina().isoformat()
        
        # Insertar en la base de datos
        insertar_evento(id_valija, evento, origen, destino, float(peso), timestamp)
        # Publicar evento en Kafka
        publicar_evento_equipaje({
            'equipaje_id': id_valija,
            'estado': evento,
            'timestamp': int(get_datetime_argentina().timestamp()),
            'origen': origen,
            'destino': destino,
            'peso': float(peso)
        })
        # Agregar a simulador para cambio de estado automático
        agregar_valija_a_simulador(id_valija, origen, destino, float(peso), evento)
        
        # Devolver resultado
        return jsonify({
            'success': True,
            'id_valija': id_valija,
            'evento': evento,
            'timestamp': timestamp,
            'origen': origen,
            'destino': destino,
            'peso': peso
        })
    except Exception as e:
        logger.error(f"Error al agregar equipaje: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/agregar_evento', methods=['POST'])
def agregar_evento():
    """
    API para agregar un evento a una valija existente.
    
    Returns:
        json: Resultado de la operación.
    """
    try:
        # Obtener datos del formulario
        id_valija = request.form.get('id_valija')
        evento = request.form.get('evento')
        timestamp = request.form.get('timestamp')
        
        # Validar datos requeridos
        if not id_valija or not evento:
            return jsonify({'error': 'Faltan datos obligatorios'}), 400
        
        # Verificar que la valija existe
        valija_eventos = obtener_valija(id_valija)
        
        if not valija_eventos:
            return jsonify({'error': 'No se encontró la valija especificada'}), 404
        
        # Obtener datos de la última entrada de la valija
        ultimo_evento = valija_eventos[0]
        origen = ultimo_evento['origen']
        destino = ultimo_evento['destino']
        peso = ultimo_evento['peso']
        
        # Usar timestamp proporcionado o generar uno nuevo
        if not timestamp:
            timestamp = get_datetime_argentina().isoformat()
        
        # Insertar nuevo evento
        insertar_evento(id_valija, evento, origen, destino, peso, timestamp)
        # Publicar evento en Kafka
        publicar_evento_equipaje({
            'equipaje_id': id_valija,
            'estado': evento,
            'timestamp': int(get_datetime_argentina().timestamp()),
            'origen': origen,
            'destino': destino,
            'peso': float(peso)
        })
        # Agregar a simulador para cambio de estado automático si corresponde
        agregar_valija_a_simulador(id_valija, origen, destino, float(peso), evento)
        
        # Devolver resultado
        return jsonify({
            'success': True,
            'id_valija': id_valija,
            'evento': evento,
            'timestamp': timestamp,
            'origen': origen,
            'destino': destino,
            'peso': peso
        })
    except Exception as e:
        logger.error(f"Error al agregar evento: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/simulador/estado')
def get_simulador_estado():
    """
    API para obtener el estado actual del simulador automático.
    
    Returns:
        json: Estado del simulador y valijas activas.
    """
    try:
        # Obtener información del simulador
        return jsonify({
            'activo': True,
            'valijas_activas': len(valijas_activas),
            'max_valijas': Config.MAX_VALIJAS_ACTIVAS,
            'intervalo_generacion': Config.INTERVALO_GENERACION,
            'timestamp': get_datetime_argentina().isoformat()
        })
    except Exception as e:
        logger.error(f"Error al obtener estado del simulador: {e}")
        return jsonify({'error': str(e), 'activo': False}), 500

@api_bp.route('/simulador/valijas_activas')
def get_simulador_valijas():
    """
    API para obtener las valijas actualmente en procesamiento por el simulador.
    
    Returns:
        json: Lista de valijas activas con sus estados.
    """
    try:
        valijas = []
        for id_valija, info in valijas_activas.items():
            # Calcular tiempo restante para próxima acción
            tiempo_restante = (info['tiempo_proxima_accion'] - get_datetime_argentina()).total_seconds()
            if tiempo_restante < 0:
                tiempo_restante = 0
            
            valijas.append({
                'id_valija': id_valija,
                'estado_actual': info['estado_actual'],
                'origen': info['origen'],
                'destino': info['destino'],
                'peso': info['peso'],
                'tiempo_proxima_accion': info['tiempo_proxima_accion'].isoformat(),
                'tiempo_restante_segundos': int(tiempo_restante)
            })
        
        return jsonify(valijas)
    except Exception as e:
        logger.error(f"Error al obtener valijas activas del simulador: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/simulador/forzar_inicio')
def forzar_inicio_simulador():
    """
    API para forzar el inicio del simulador automático.
    Útil para iniciar el simulador desde una ruta web.
    """
    try:
        # Forzar la activación del simulador independientemente del entorno
        os.environ['START_SIMULATOR'] = 'True'
        logger.info("Forzando inicio del simulador mediante API")
        
        # Intentar iniciar el simulador
        simulador_iniciado = iniciar_simulador()
        
        if simulador_iniciado:
            return jsonify({
                'success': True,
                'mensaje': 'Simulador iniciado correctamente',
                'timestamp': get_datetime_argentina().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo iniciar el simulador',
                'timestamp': get_datetime_argentina().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error al forzar inicio del simulador: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': get_datetime_argentina().isoformat()
        }), 500