"""
Script para inspeccionar la base de datos SQLite y listar las tablas existentes.
"""
import sqlite3
import os

DB_PATH = os.path.join('data', 'equipajes.db')

if not os.path.exists(DB_PATH):
    print(f"No se encontró la base de datos en {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Tablas en la base de datos:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print(row)

print("\nEsquema de la tabla eventos_equipaje:")
cursor.execute("PRAGMA table_info(eventos_equipaje)")
for col in cursor.fetchall():
    print(col)

conn.close()
