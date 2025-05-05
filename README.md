# Sistema de Gestión de Equipajes

Un sistema web responsivo para la gestión y seguimiento de equipajes en tiempo real para aeropuertos y aerolíneas.

**🌐 [Acceder al sistema en vivo](https://fedeegea.pythonanywhere.com/)**

![Sistema de Gestión de Equipajes]([https://via.placeholder.com/800x400?text=Sistema+de+Gesti%C3%B3n+de+Equipajes](https://github.com/fedeegea/ArqApp-03/blob/main/dashboard.png))

## Características

- 📊 **Dashboard en tiempo real**: Visualiza estadísticas y métricas principales de los equipajes en el sistema.
- 🧳 **Seguimiento de equipajes**: Monitorea el estado actual e historial de cada equipaje.
- 🗺️ **Visualización en mapa**: Ubica los equipajes en un mapa según su estado y ubicación.
- ➕ **Registro manual**: Permite agregar equipajes y eventos manualmente.
- 🤖 **Simulador automático**: Genera y procesa eventos de equipaje de forma automática.
- 📱 **Diseño responsivo**: Funciona perfectamente en dispositivos móviles y de escritorio.

## Tecnologías utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos**: SQLite
- **Visualización**: Chart.js, Leaflet.js
- **Simulación**: Hilos (threading) de Python

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. Clona este repositorio:

```bash
git clone https://github.com/fedeegea/ArqApp-03.git
cd ArqApp-03
```

2. Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En MacOS/Linux
source venv/bin/activate
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Inicializa la base de datos (si no existe):

```bash
python setup_db.py
```

## Uso

### Iniciar la aplicación web

Para iniciar la aplicación Flask, simplemente ejecuta:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Funcionalidades principales

1. **Dashboard**: La página principal muestra estadísticas en tiempo real y eventos recientes.
2. **Seguimiento de Valijas**: Consulta información detallada de equipajes específicos.
3. **Mapa de Equipajes**: Visualiza la ubicación y estado de los equipajes en un mapa interactivo.
4. **Agregar Equipajes**: Registra nuevos equipajes o eventos manualmente.

### Simulador automático

El sistema incluye un simulador que genera y procesa equipajes automáticamente:

- Se inicia automáticamente con la aplicación Flask
- Genera nuevos equipajes cada 15 segundos (configurable)
- Procesa los estados (escaneado → cargado → entregado)
- Mantiene hasta 20 valijas activas simultáneamente
- El estado del simulador se puede monitorear en el dashboard

## Estructura del proyecto

```
ArqApp-03/
│
├── app.py                 # Aplicación principal Flask
├── consumer.py            # Consumidor de eventos (opcional)
├── producer.py            # Generador de eventos (opcional)
├── simulador_auto.py      # Simulador automático de eventos
├── setup_db.py            # Script para inicializar la base de datos
├── equipajes.db           # Base de datos SQLite
├── requirements.txt       # Dependencias del proyecto
├── generar_datos_prueba.py # Script para generar datos de prueba
├── docker-compose.yml     # Configuración para despliegue con Docker
│
├── static/                # Archivos estáticos
│   ├── css/              
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── templates/             # Plantillas HTML
    ├── base.html
    ├── index.html         # Dashboard
    ├── valijas.html       # Seguimiento de valijas
    ├── mapa.html          # Visualización en mapa
    └── agregar.html       # Registro manual
```

## Despliegue en producción

Para desplegar esta aplicación en un entorno de producción, se recomienda:

1. Usar un servidor WSGI como Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app
   ```

2. Configurar un servidor web como Nginx como proxy reverso.

3. Considerar una base de datos más robusta como PostgreSQL o MySQL para entornos con alta carga.

### Despliegue con Docker

El proyecto incluye un archivo `docker-compose.yml` para facilitar el despliegue con Docker:

```bash
# Construir y levantar los contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener contenedores
docker-compose down
```

## Contribuir

Las contribuciones son bienvenidas! Para contribuir:

1. Haz un fork del repositorio.
2. Crea una rama para tu función (`git checkout -b feature/nueva-funcion`).
3. Realiza tus cambios y hazles commit (`git commit -am 'Agrega nueva función'`).
4. Sube tus cambios a tu repositorio (`git push origin feature/nueva-funcion`).
5. Abre un Pull Request.

## Contacto

Para preguntas o soporte, por favor contacta a través de:
- Email: fegea@uade.edu.ar
- GitHub: [tu-usuario](https://github.com/fedeegea)
