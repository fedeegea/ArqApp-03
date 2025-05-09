#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aplicación web Flask para el Sistema de Gestión de Equipajes
Proporciona una interfaz gráfica para monitorear los eventos de equipaje
"""

import os
import sys
import logging
from flask import Flask, render_template, redirect, url_for

# Ajustar el path para las importaciones
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basedir)

# Importar componentes del sistema reorganizado
from src.core.config import Config, get_datetime_argentina
from src.core.db_service import inicializar_db
from src.simulador.simulador_auto import iniciar_simulador
from src.api.routes import api_bp
# Agregar import para el productor Kafka
from src.eda.productor_kafka import publicar_evento_equipaje

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app')

# Crear la aplicación Flask
app = Flask(__name__)

# Registrar el blueprint de las rutas API con prefijo /api
app.register_blueprint(api_bp, url_prefix='/api')

@app.context_processor
def utility_processor():
    """
    Funciones y variables disponibles en todos los templates.
    """
    return {
        'fecha_actual': get_datetime_argentina().strftime("%d de %B de %Y")
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

# Manejador de errores para rutas no encontradas
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Manejador de errores para errores internos
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

def inicializar_aplicacion():
    """Inicializa la aplicación y sus componentes"""
    # Verificar si la base de datos existe, si no, crearla
    if not os.path.exists(Config.DB_PATH):
        try:
            inicializar_db()
        except Exception as e:
            logger.error(f"Error al crear la base de datos: {e}")

    # En desarrollo local, siempre activar el simulador automáticamente a menos que se desactive explícitamente
    if os.environ.get('DISABLE_SIMULATOR', 'False') != 'True':
        try:
            logger.info("Iniciando simulador automático de equipajes...")
            # Forzar la variable de entorno a True para asegurar que el simulador se inicie
            os.environ['START_SIMULATOR'] = 'True'
            simulador_iniciado = iniciar_simulador()
            if simulador_iniciado:
                logger.info("Simulador automático iniciado correctamente")
            else:
                logger.warning("No se pudo iniciar el simulador automático")
        except Exception as e:
            logger.error(f"Error al iniciar el simulador: {e}")

# Solo iniciar el simulador si se ejecuta directamente o si se solicita explícitamente
if __name__ == '__main__':
    # Inicializar la aplicación
    inicializar_aplicacion()
    
    # Ejecutar la aplicación en modo debug solo en desarrollo local
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
else:
    # Para WSGI (PythonAnywhere, etc.)
    inicializar_aplicacion()