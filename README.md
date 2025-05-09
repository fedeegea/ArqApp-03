# Sistema de Gestión de Equipajes

Sistema web para la gestión, seguimiento y visualización de equipajes en tiempo real, con arquitectura orientada a eventos (EDA) usando Kafka.

---

## Características principales
- Dashboard en tiempo real con estadísticas y eventos recientes.
- Seguimiento detallado e historial de cada equipaje.
- Visualización de estados y ubicación en mapa interactivo.
- Registro manual y simulador automático de equipajes.
- Arquitectura orientada a eventos (EDA) con Kafka para robustez y reportes automáticos.
- Reporte automático de equipajes perdidos (CSV).
- Manejo avanzado de errores y reintentos en frontend.
- Logo institucional y experiencia de usuario mejorada.

## Tecnologías
- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, Leaflet.js
- **Base de datos:** SQLite
- **EDA:** Kafka (KRaft mode, sin Zookeeper), kafka-python

## Arquitectura orientada a eventos (EDA)

- **Productor Kafka:** El backend Flask publica eventos de equipaje en el tópico `eventos_equipaje`.
- **Consumidor Kafka:** Microservicio Python que detecta equipajes perdidos y genera reportes automáticos en CSV.
- **Simulador:** Genera equipajes y simula su ciclo de vida, incluyendo pérdidas aleatorias.

### Flujo de eventos
1. El backend publica cada cambio de estado de equipaje en Kafka.
2. El consumidor Kafka mantiene el estado de cada equipaje y detecta pérdidas.
3. Si un equipaje pasa a "perdido", se genera un reporte automático en CSV.

## Instalación y ejecución

### Prerrequisitos
- Python 3.8+
- Kafka (modo KRaft, sin Zookeeper)
- pip

### Pasos
1. Clona el repositorio y entra al directorio:
   ```bash
   git clone https://github.com/fedeegea/ArqApp-03.git
   cd ArqApp-03
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicia Kafka (ver README para Windows/KRaft).
4. Ejecuta la app Flask:
   ```bash
   python app.py
   ```
5. (En otra terminal) Ejecuta el consumidor Kafka:
   ```bash
   python src/eda/consumidor_kafka.py
   ```

## Estructura del proyecto

- `app.py`: App principal Flask
- `src/api/routes.py`: Rutas API REST
- `src/core/db_service.py`: Acceso a base de datos SQLite
- `src/eda/productor_kafka.py`: Productor Kafka
- `src/eda/consumidor_kafka.py`: Consumidor Kafka y reporte de pérdidas
- `src/simulador/simulador_auto.py`: Simulador automático de equipajes
- `static/`, `templates/`: Frontend y vistas
- `data/equipajes.db`: Base de datos SQLite

## Uso y funcionalidades
- Dashboard: Estadísticas y eventos recientes
- Seguimiento: Consulta de historial y estado de valijas
- Mapa: Visualización geográfica y filtros avanzados
- Agregar: Registro manual de equipajes y eventos
- Simulador: Generación automática de equipajes y estados
- Reporte CSV: Generación automática al detectar equipaje perdido

## Kafka en Windows (KRaft)
- Descarga Kafka y descomprime.
- Inicia el broker con:
  ```bash
  .\bin\windows\kafka-server-start.bat .\config\kafka-server.properties
  ```
- Asegúrate de que el puerto 9092 esté libre y usa IPv4.

## Solución de problemas
- Si ves "Error al cargar datos del servidor" en el frontend, revisa:
  - Conexión a la base de datos
  - Logs del backend Flask
  - Estado del broker Kafka
  - Formato de los datos en la base
- El frontend ahora es robusto ante datos incompletos y muestra mensajes claros.

## Despliegue
- Compatible con PythonAnywhere, Docker y despliegue local.
- Incluye archivo `docker-compose.yml` para despliegue rápido.

## Contacto
- Email: fegea@uade.edu.ar
- GitHub: [fedeegea](https://github.com/fedeegea)

---

**Actualizado: 2025**
