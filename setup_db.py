#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para configurar la base de datos SQLite para el sistema de gestión de equipajes.
Crea la tabla eventos_equipaje que almacenará todos los eventos relacionados con el equipaje.
"""

import sqlite3
import os
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('setup_db')

# Ruta de la base de datos
DB_PATH = 'equipajes.db'

def crear_base_datos():
    """
    Crea la base de datos SQLite y la tabla eventos_equipaje si no existen.
    """
    try:
        # Verificar si la base de datos ya existe
        db_exists = os.path.exists(DB_PATH)
        
        # Conectar a la base de datos (se crea si no existe)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear tabla eventos_equipaje
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos_equipaje (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            id_valija TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            origen TEXT,
            destino TEXT,
            peso REAL
        )
        ''')
        
        # Crear índices para mejorar el rendimiento de las consultas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_evento ON eventos_equipaje (evento)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_id_valija ON eventos_equipaje (id_valija)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON eventos_equipaje (timestamp)')
        
        conn.commit()
        
        if not db_exists:
            logger.info(f"Base de datos creada exitosamente en {DB_PATH}")
        else:
            logger.info(f"Conectado a la base de datos existente en {DB_PATH}")
        
        logger.info("Tabla eventos_equipaje configurada correctamente")
        
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al configurar la base de datos: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Iniciando configuración de la base de datos...")
    crear_base_datos()
    logger.info("Configuración de la base de datos completada")