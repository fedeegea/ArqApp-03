"""
Archivo WSGI para PythonAnywhere - Sistema de Gestión de Equipajes (Versión con diagnóstico)
"""

import sys
import os
import traceback

# Imprimir información de diagnóstico al log
print("Iniciando archivo WSGI - Sistema de Gestión de Equipajes", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Python path antes de modificar: {sys.path}", file=sys.stderr)

# Directorio del proyecto
path = '/home/fedeegea/ArqApp-03'
if path not in sys.path:
    sys.path.insert(0, path)

print(f"Directorio del proyecto: {path}", file=sys.stderr)
print(f"Python path después de modificar: {sys.path}", file=sys.stderr)

# Listar contenido del directorio para diagnóstico
try:
    print(f"Contenido del directorio del proyecto:", file=sys.stderr)
    for item in os.listdir(path):
        print(f"  - {item}", file=sys.stderr)
    
    # Verificar archivos críticos
    app_py = os.path.join(path, 'app.py')
    if os.path.exists(app_py):
        print(f"✓ El archivo app.py existe: {app_py}", file=sys.stderr)
    else:
        print(f"✗ El archivo app.py NO existe: {app_py}", file=sys.stderr)
    
    src_dir = os.path.join(path, 'src')
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        print(f"✓ El directorio src existe: {src_dir}", file=sys.stderr)
        # Listar contenido de src
        print(f"Contenido del directorio src:", file=sys.stderr)
        for item in os.listdir(src_dir):
            print(f"  - {item}", file=sys.stderr)
    else:
        print(f"✗ El directorio src NO existe: {src_dir}", file=sys.stderr)
except Exception as e:
    print(f"Error al listar directorios: {e}", file=sys.stderr)

# Activar el entorno virtual
try:
    activate_this = os.path.join(path, 'venv/bin/activate_this.py')
    if os.path.exists(activate_this):
        with open(activate_this) as file_:
            exec(file_.read(), dict(__file__=activate_this))
        print(f"✓ Entorno virtual activado: {activate_this}", file=sys.stderr)
    else:
        print(f"✗ Archivo de activación no encontrado: {activate_this}", file=sys.stderr)
except Exception as e:
    print(f"Error al activar el entorno virtual: {e}", file=sys.stderr)
    # Continuar aunque falle la activación

# Configurar simulador automático
os.environ['START_SIMULATOR'] = 'True'
print("Variable START_SIMULATOR configurada como 'True'", file=sys.stderr)

# Intentar importar manualmente antes de importar app.py
try:
    print("Verificando importaciones críticas...", file=sys.stderr)
    import flask
    print(f"✓ Flask importado (versión: {flask.__version__})", file=sys.stderr)
    
    # Probar la importación de src
    try:
        import src
        print("✓ Módulo src importado", file=sys.stderr)
    except ImportError as e:
        print(f"✗ Error al importar módulo src: {e}", file=sys.stderr)
        # Crear __init__.py si no existe
        try:
            init_path = os.path.join(path, 'src', '__init__.py')
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write("# Archivo de inicialización para el paquete src\n")
                print(f"Creado archivo __init__.py en {os.path.dirname(init_path)}", file=sys.stderr)
        except Exception as e2:
            print(f"Error al crear __init__.py: {e2}", file=sys.stderr)
except Exception as e:
    print(f"Error en verificación de importaciones: {e}", file=sys.stderr)

# Importar la aplicación Flask con manejo detallado de errores
try:
    print("Intentando importar app.py...", file=sys.stderr)
    from app import app as application
    print("✓ Aplicación Flask importada correctamente", file=sys.stderr)
except Exception as e:
    print(f"ERROR al importar la aplicación Flask: {e}", file=sys.stderr)
    print(f"Traceback completo:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Intentar una solución alternativa si el error es de importación
    if "No module named 'src'" in str(e) or "No module named 'src.core'" in str(e):
        print("Intentando solución alternativa para el error de importación...", file=sys.stderr)
        try:
            # Modificar sys.path para incluir src y sus subdirectorios
            src_path = os.path.join(path, 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            # Incluir también los subdirectorios
            for subdir in ['core', 'api', 'simulador']:
                subdir_path = os.path.join(src_path, subdir)
                if os.path.isdir(subdir_path) and subdir_path not in sys.path:
                    sys.path.insert(0, subdir_path)
            
            print(f"Path modificado: {sys.path}", file=sys.stderr)
            
            # Intento alternativo de importación
            print("Reintentando importar app.py...", file=sys.stderr)
            from app import app as application
            print("✓ Importación exitosa después de la solución alternativa", file=sys.stderr)
        except Exception as e2:
            print(f"La solución alternativa también falló: {e2}", file=sys.stderr)
            raise
    else:
        # Si no es un error de importación de src, reenviar la excepción
        raise