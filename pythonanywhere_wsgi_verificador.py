"""
Archivo WSGI para PythonAnywhere - verificador de configuración
Copia este contenido en tu archivo WSGI de PythonAnywhere
"""

import sys
import os

# Agregar el directorio del proyecto al path
path = '/home/fedeegea/ArqApp-03'
if path not in sys.path:
    sys.path.insert(0, path)

# Verificar si los archivos principales existen
files_to_check = ['app.py', 'simulador_auto.py', 'requirements.txt']
missing_files = []
for file in files_to_check:
    if not os.path.exists(os.path.join(path, file)):
        missing_files.append(file)

# Importar la aplicación Flask
try:
    from app import app as application
    # Configurar para producción
    application.config['DEBUG'] = False
    
    # Si quieres activar el simulador automático, descomenta la siguiente línea:
    #os.environ['START_SIMULATOR'] = 'True'
    
    # Agregar un mensaje en los logs para verificar que se cargó correctamente
    print("WSGI: Aplicación Flask cargada correctamente", file=sys.stderr)
    
except Exception as e:
    # Si hay un error al importar, mostrarlo claramente
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = f'''
        <html>
        <head><title>Error de configuración en PythonAnywhere</title></head>
        <body>
            <h1>Error al cargar la aplicación Flask</h1>
            <p>Se encontró un error al cargar la aplicación:</p>
            <pre>{str(e)}</pre>
            
            <h2>Verificación de archivos</h2>
            <p>Directorio del proyecto: {path}</p>
            {'<p>✅ Todos los archivos principales existen.</p>' if not missing_files else 
            '<p>❌ Faltan algunos archivos necesarios: ' + ', '.join(missing_files) + '</p>'}
            
            <h2>Path de Python</h2>
            <pre>{sys.path}</pre>
            
            <h2>Solución</h2>
            <p>Revisa los logs de error para más detalles y verifica que todos los archivos
            están correctamente subidos al servidor.</p>
        </body>
        </html>
        '''.encode('utf-8')
        response_headers = [('Content-type', 'text/html; charset=utf-8'),
                          ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]