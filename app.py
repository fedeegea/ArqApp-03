#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplicación web Flask para el Sistema de Gestión de Equipajes
Proporciona una interfaz gráfica para monitorear los eventos de equipaje
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import uuid
import os
import sys
import simulador_auto  # Importamos el módulo de simulación automática

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('flask-app')

# Crear la aplicación Flask
app = Flask(__name__)

# Detectar si estamos en PythonAnywhere
ON_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or os.path.exists('/var/www')

# Configuración de la base de datos
# En PythonAnywhere, usamos una ruta absoluta
if ON_PYTHONANYWHERE:
    base_dir = '/home/fedeegea/ArqApp-03'
    DB_PATH = os.path.join(base_dir, 'equipajes.db')
    # Para debug
    logger.info(f"Ejecutando en PythonAnywhere. DB_PATH: {DB_PATH}")
    logger.info(f"START_SIMULATOR está configurado como: {os.environ.get('START_SIMULATOR', 'No configurado')}")
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

@app.context_processor
def utility_processor():
    """
    Funciones y variables disponibles en todos los templates.
    """
    return {
        'fecha_actual': datetime.now().strftime("%d de %B de %Y")
    }

@app.route('/')
def index():
    """
    Ruta principal que muestra el dashboard.
    """
    return render_template('index.html')

@app.route('/valijas')
def valijas():
    """
    Ruta que muestra la página de seguimiento de valijas.
    """
    return render_template('valijas.html')

@app.route('/agregar')
def agregar():
    """
    Ruta que muestra la página para agregar equipajes manualmente.
    """
    return render_template('agregar.html')

@app.route('/mapa')
def mapa():
    """
    Ruta que muestra la página con el mapa de equipajes.
    """
    return render_template('mapa.html')

@app.route('/api/eventos')
def get_eventos():
    """
    API para obtener los eventos de equipaje.
    
    Returns:
        json: Lista de eventos en formato JSON.
    """
    try:
        conn = get_db_connection()
        eventos = conn.execute('SELECT * FROM eventos_equipaje ORDER BY timestamp DESC LIMIT 100').fetchall()
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        resultado = [dict(evento) for evento in eventos]
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener eventos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/estadisticas')
def get_estadisticas():
    """
    API para obtener estadísticas de eventos.
    
    Returns:
        json: Estadísticas en formato JSON.
    """
    try:
        conn = get_db_connection()
        
        # Contar eventos por tipo
        eventos_por_tipo = conn.execute(
            'SELECT evento, COUNT(*) as cantidad FROM eventos_equipaje GROUP BY evento'
        ).fetchall()
        
        # Contar eventos de las últimas 24 horas
        fecha_limite = (datetime.now() - timedelta(hours=24)).isoformat()
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
        
        resultado = {
            'por_tipo': tipos,
            'ultimas_24h': eventos_recientes['cantidad'],
            'valijas_unicas': valijas_unicas['cantidad']
        }
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos_tiempo')
def get_eventos_tiempo():
    """
    API para obtener eventos agrupados por intervalos de tiempo.
    
    Returns:
        json: Eventos por tiempo en formato JSON.
    """
    try:
        conn = get_db_connection()
        eventos = conn.execute('SELECT * FROM eventos_equipaje ORDER BY timestamp').fetchall()
        conn.close()
        
        # Convertir a pandas DataFrame para facilitar el análisis
        df = pd.DataFrame([dict(evento) for evento in eventos])
        
        # Si no hay datos, devolver lista vacía
        if df.empty:
            return jsonify([])
        
        # Convertir timestamp a datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Agrupar por intervalos de 5 minutos
        df['intervalo'] = df['timestamp'].dt.floor('5min')
        
        # Contar eventos por intervalo
        eventos_por_tiempo = df.groupby(['intervalo', 'evento']).size().reset_index(name='cantidad')
        
        # Formatear para la respuesta
        resultado = []
        for _, row in eventos_por_tiempo.iterrows():
            resultado.append({
                'intervalo': row['intervalo'].isoformat(),
                'evento': row['evento'],
                'cantidad': int(row['cantidad'])
            })
        
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener eventos por tiempo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/valija/<id_valija>')
def get_valija(id_valija):
    """
    API para obtener el historial de una valija específica.
    
    Args:
        id_valija (str): ID de la valija a consultar.
        
    Returns:
        json: Historial de eventos de la valija en formato JSON.
    """
    try:
        conn = get_db_connection()
        eventos = conn.execute(
            'SELECT * FROM eventos_equipaje WHERE id_valija = ? ORDER BY timestamp',
            (id_valija,)
        ).fetchall()
        conn.close()
        
        # Convertir los objetos Row a diccionarios
        resultado = [dict(evento) for evento in eventos]
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener información de valija {id_valija}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/valijas')
def get_valijas():
    """
    API para obtener la lista de todas las valijas.
    
    Returns:
        json: Lista de valijas en formato JSON.
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
        resultado = [dict(valija) for valija in valijas]
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error al obtener lista de valijas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/agregar_equipaje', methods=['POST'])
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
        id_valija = str(uuid.uuid4())
        
        # Usar timestamp proporcionado o generar uno nuevo
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Insertar en la base de datos
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

@app.route('/api/agregar_evento', methods=['POST'])
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
        conn = get_db_connection()
        valija = conn.execute(
            'SELECT * FROM eventos_equipaje WHERE id_valija = ? ORDER BY timestamp DESC LIMIT 1',
            (id_valija,)
        ).fetchone()
        
        if not valija:
            conn.close()
            return jsonify({'error': 'No se encontró la valija especificada'}), 404
        
        # Obtener datos de la valija
        origen = valija['origen']
        destino = valija['destino']
        peso = valija['peso']
        
        # Usar timestamp proporcionado o generar uno nuevo
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # Insertar nuevo evento
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

@app.route('/api/simulador/estado')
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
            'valijas_activas': len(simulador_auto.valijas_activas),
            'max_valijas': simulador_auto.MAX_VALIJAS_ACTIVAS,
            'intervalo_generacion': simulador_auto.INTERVALO_GENERACION,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error al obtener estado del simulador: {e}")
        return jsonify({'error': str(e), 'activo': False}), 500

@app.route('/api/simulador/valijas_activas')
def get_simulador_valijas():
    """
    API para obtener las valijas actualmente en procesamiento por el simulador.
    
    Returns:
        json: Lista de valijas activas con sus estados.
    """
    try:
        valijas = []
        for id_valija, info in simulador_auto.valijas_activas.items():
            # Calcular tiempo restante para próxima acción
            tiempo_restante = (info['tiempo_proxima_accion'] - datetime.now()).total_seconds()
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

@app.route('/api/simulador/forzar_inicio')
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
        simulador_iniciado = simulador_auto.iniciar_simulador()
        
        if simulador_iniciado:
            return jsonify({
                'success': True,
                'mensaje': 'Simulador iniciado correctamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo iniciar el simulador',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error al forzar inicio del simulador: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Manejador de errores para rutas no encontradas
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Manejador de errores para errores internos
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Solo iniciar el simulador si no estamos en PythonAnywhere o si explícitamente se solicita
if __name__ == '__main__' or os.environ.get('START_SIMULATOR', 'False') == 'True':
    # Verificar si la base de datos existe, si no, crearla
    if not os.path.exists(DB_PATH):
        try:
            logger.info(f"Creando base de datos {DB_PATH}")
            conn = sqlite3.connect(DB_PATH)
            conn.execute('''
                CREATE TABLE eventos_equipaje (
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
        except Exception as e:
            logger.error(f"Error al crear la base de datos: {e}")
    
    # Importar e iniciar el simulador automático si no estamos en PythonAnywhere
    # o si explícitamente lo solicitamos
    try:
        logger.info("Iniciando simulador automático de equipajes...")
        simulador_iniciado = simulador_auto.iniciar_simulador()
        if simulador_iniciado:
            logger.info("Simulador automático iniciado correctamente")
        else:
            logger.warning("No se pudo iniciar el simulador automático")
    except Exception as e:
        logger.error(f"Error al iniciar el simulador: {e}")
    
    # Ejecutar la aplicación en modo debug solo en desarrollo local
    if not ON_PYTHONANYWHERE:
        app.run(debug=True, host='0.0.0.0', port=5000)