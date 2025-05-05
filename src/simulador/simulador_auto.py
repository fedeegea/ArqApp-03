"""
Módulo para simular la generación y procesamiento automático de eventos de equipaje
sin necesidad de ejecutar producer.py y consumer.py manualmente.
"""

import threading
import time
import random
import uuid
import logging
from datetime import datetime, timedelta
import os
import sys

# Ajustar el path para las importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar componentes centralizados
from src.core.config import Config, get_datetime_argentina
from src.core.db_service import insertar_evento, obtener_valijas_incompletas, inicializar_db

# Configuración de logging
logger = logging.getLogger('simulador-auto')

# Estados de seguimiento de las valijas
valijas_activas = {}  # Diccionario para mantener el estado de las valijas activas

def generar_nuevo_equipaje():
    """Genera un nuevo equipaje con evento inicial (escaneado)."""
    id_valija = str(uuid.uuid4())
    origen = random.choice(Config.AEROPUERTOS)
    
    # Asegurar que destino sea diferente al origen
    destinos_posibles = [a for a in Config.AEROPUERTOS if a != origen]
    destino = random.choice(destinos_posibles)
    
    peso = round(random.uniform(5, 30), 1)  # Peso entre 5 y 30 kg
    
    # Insertar evento de escaneado usando el servicio de base de datos
    insertar_evento(id_valija, 'equipaje_escaneado', origen, destino, peso)
    
    # Agregar a valijas activas con tiempo estimado para próximo evento
    tiempo_proxima_accion = get_datetime_argentina() + timedelta(seconds=random.randint(30, 120))
    valijas_activas[id_valija] = {
        'id': id_valija,
        'origen': origen,
        'destino': destino,
        'peso': peso,
        'estado_actual': 'equipaje_escaneado',
        'tiempo_proxima_accion': tiempo_proxima_accion
    }
    
    return id_valija

def procesar_equipajes_activos():
    """Procesa las valijas activas y genera eventos según corresponda."""
    # Lista para almacenar valijas a eliminar
    valijas_a_eliminar = []
    
    # Verificar cada valija activa
    for id_valija, info in valijas_activas.items():
        # Si es hora de la próxima acción
        if get_datetime_argentina() >= info['tiempo_proxima_accion']:
            estado_actual = info['estado_actual']
            
            # Determinar próximo estado según el estado actual
            if estado_actual == 'equipaje_escaneado':
                # Cambiar a estado cargado
                insertar_evento(id_valija, 'equipaje_cargado', 
                               info['origen'], info['destino'], info['peso'])
                
                # Actualizar estado y programar próxima acción
                info['estado_actual'] = 'equipaje_cargado'
                info['tiempo_proxima_accion'] = get_datetime_argentina() + timedelta(
                    seconds=random.randint(60, 180))
                
            elif estado_actual == 'equipaje_cargado':
                # Cambiar a estado entregado
                insertar_evento(id_valija, 'equipaje_entregado', 
                               info['origen'], info['destino'], info['peso'])
                
                # Marcar para eliminar de valijas activas
                valijas_a_eliminar.append(id_valija)
    
    # Eliminar valijas completadas
    for id_valija in valijas_a_eliminar:
        del valijas_activas[id_valija]
        logger.info(f"Valija {id_valija} completó el ciclo y fue eliminada de activas")

def cargar_estado_inicial():
    """Carga el estado de valijas existentes en la base de datos."""
    try:
        # Obtener valijas que no han completado su ciclo usando el servicio de base de datos
        valijas_incompletas = obtener_valijas_incompletas()
        
        # Agregar valijas incompletas al seguimiento
        for valija in valijas_incompletas:
            id_valija = valija['id_valija']
            
            # Verificar si ya está en las activas
            if id_valija in valijas_activas:
                continue
                
            # Agregar a valijas activas
            tiempo_proxima_accion = get_datetime_argentina() + timedelta(seconds=random.randint(30, 120))
            valijas_activas[id_valija] = {
                'id': id_valija,
                'origen': valija['origen'],
                'destino': valija['destino'],
                'peso': valija['peso'],
                'estado_actual': valija['evento'],
                'tiempo_proxima_accion': tiempo_proxima_accion
            }
            
        logger.info(f"Se cargaron {len(valijas_incompletas)} valijas incompletas para seguimiento")
    except Exception as e:
        logger.error(f"Error al cargar estado inicial: {e}")

def simulador_eventos():
    """Función principal que ejecuta el simulador de eventos."""
    logger.info("Iniciando simulador automático de eventos de equipaje")
    
    # Cargar estado inicial
    cargar_estado_inicial()
    
    # Variable para controlar cuándo generar nueva valija
    ultima_generacion = get_datetime_argentina() - timedelta(seconds=Config.INTERVALO_GENERACION)
    
    try:
        while True:
            # Procesar equipajes activos existentes
            procesar_equipajes_activos()
            
            # Generar nueva valija si es tiempo y no excedemos el límite
            if (get_datetime_argentina() - ultima_generacion).total_seconds() >= Config.INTERVALO_GENERACION and \
               len(valijas_activas) < Config.MAX_VALIJAS_ACTIVAS:
                generar_nuevo_equipaje()
                ultima_generacion = get_datetime_argentina()
                logger.info(f"Valijas activas: {len(valijas_activas)}")
            
            # Breve pausa para no saturar la CPU
            time.sleep(5)
            
    except Exception as e:
        logger.error(f"Error en el simulador: {e}")
    finally:
        logger.info("Simulador detenido")

def iniciar_simulador():
    """Inicia el simulador en un hilo separado."""
    try:
        # Verificar si la base de datos existe
        logger.info(f"Verificando si la base de datos existe en: {Config.DB_PATH}")
        if not os.path.exists(Config.DB_PATH):
            # Intentar crearla
            if not inicializar_db():
                logger.error(f"No se pudo inicializar la base de datos. No se puede iniciar el simulador.")
                return False
        
        # Si estamos en PythonAnywhere, siempre forzar la activación del simulador
        if Config.ON_PYTHONANYWHERE:
            # Forzar la variable de entorno a True para asegurar que el simulador se inicie
            os.environ['START_SIMULATOR'] = 'True'
            logger.info("Forzando la activación del simulador en PythonAnywhere")
        
        # Crear y arrancar el hilo del simulador con más protección
        try:
            logger.info("Creando hilo del simulador...")
            # Usar non-daemon thread para evitar que sea terminado automáticamente
            hilo_simulador = threading.Thread(target=simulador_eventos, daemon=False)
            logger.info("Iniciando hilo del simulador...")
            hilo_simulador.start()
            logger.info("Hilo del simulador iniciado correctamente")
            
            # Generar un equipaje inmediatamente para verificar que el simulador está funcionando
            try:
                id_valija = generar_nuevo_equipaje()
                logger.info(f"Equipaje inicial generado con ID: {id_valija}. Total valijas activas: {len(valijas_activas)}")
            except Exception as e:
                logger.error(f"Error al generar equipaje inicial: {e}")
            
            return True
        except Exception as thread_error:
            logger.error(f"Error al iniciar el hilo del simulador: {thread_error}")
            return False
            
    except Exception as e:
        logger.error(f"Error general al iniciar el simulador: {e}")
        return False

# Para pruebas independientes
if __name__ == "__main__":
    iniciar_simulador()
    try:
        # Mantener el programa principal vivo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulador detenido por el usuario")