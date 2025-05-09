/**
 * Script principal para funcionalidades compartidas del Sistema de Gestión de Equipajes
 */

// Mapa de aeropuertos con coordenadas reales para visualización
const aeropuertosCoords = {
    'EZE - Buenos Aires': [-34.8222, -58.5358],
    'AEP - Buenos Aires': [-34.5598, -58.4165],
    'COR - Córdoba': [-31.3236, -64.2081],
    'MDZ - Mendoza': [-32.8312, -68.7929],
    'BRC - Bariloche': [-41.1335, -71.3208],
    'USH - Ushuaia': [-54.8431, -68.3132],
    'MAD - Madrid': [40.4983, -3.5676],
    'BCN - Barcelona': [41.2974, 2.0833],
    'MIA - Miami': [25.7932, -80.2906],
    'JFK - Nueva York': [40.6413, -73.7781]
};

// Función para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast show animate__animated animate__fadeIn`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const tipoIcono = {
        'info': 'info-circle text-primary',
        'success': 'check-circle text-success',
        'warning': 'exclamation-triangle text-warning',
        'danger': 'exclamation-circle text-danger'
    };
    
    const icono = tipoIcono[tipo] || tipoIcono.info;
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${icono} me-2"></i>
            <strong class="me-auto">Sistema de Gestión de Equipajes</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${mensaje}
        </div>
    `;
    
    const contenedor = document.getElementById('notificaciones-container');
    if (!contenedor) {
        const nuevoContenedor = document.createElement('div');
        nuevoContenedor.id = 'notificaciones-container';
        nuevoContenedor.style.position = 'fixed';
        nuevoContenedor.style.top = '70px';
        nuevoContenedor.style.right = '20px';
        nuevoContenedor.style.zIndex = '1050';
        nuevoContenedor.style.maxWidth = '350px';
        document.body.appendChild(nuevoContenedor);
        
        nuevoContenedor.appendChild(toast);
    } else {
        contenedor.appendChild(toast);
    }
    
    // Auto cerrar después de 5 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('animate__fadeOut');
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 5000);
}

// Función para formatear fechas ISO a formato local
function formatearFecha(fechaISO) {
    if (!fechaISO) return 'N/A';
    
    const fecha = new Date(fechaISO);
    return fecha.toLocaleString();
}

// Función para convertir objetos a formato de URL
function objectToURLParams(obj) {
    return Object.keys(obj)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(obj[key]))
        .join('&');
}

// Función para obtener parámetros de la URL
function obtenerParametrosURL() {
    const params = {};
    const query = window.location.search.substring(1);
    const vars = query.split('&');
    
    for (let i = 0; i < vars.length; i++) {
        if (vars[i] === '') continue;
        
        const pair = vars[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    
    return params;
}

// Función para actualizar la barra de navegación activa
function actualizarNavActivo() {
    // Obtener la ruta actual
    const path = window.location.pathname;
    
    // Remover la clase activa de todos los enlaces
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Agregar la clase activa al enlace correspondiente
    if (path === '/' || path === '/index.html') {
        document.querySelector('.nav-link[href="/"]')?.classList.add('active');
    } else {
        document.querySelector(`.nav-link[href="${path}"]`)?.classList.add('active');
    }
}

// Función para validar formularios
function validarFormulario(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let valido = true;
    const campos = form.querySelectorAll('[required]');
    
    campos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.classList.add('is-invalid');
            valido = false;
        } else {
            campo.classList.remove('is-invalid');
        }
    });
    
    return valido;
}

// Función para obtener posición en el mapa basada en aeropuerto
function obtenerPosicionAeropuerto(nombreAeropuerto) {
    // Si el aeropuerto está en nuestro mapa, devolver sus coordenadas
    if (aeropuertosCoords[nombreAeropuerto]) {
        return aeropuertosCoords[nombreAeropuerto];
    }
    
    // Si no lo encontramos, devolver una posición aleatoria cerca de Buenos Aires
    const posBase = [-34.6037, -58.3816]; // Buenos Aires
    const offsetLat = (Math.random() - 0.5) * 2;
    const offsetLng = (Math.random() - 0.5) * 2;
    
    return [posBase[0] + offsetLat, posBase[1] + offsetLng];
}

// Función para colorear marcadores según el estado del equipaje
function obtenerColorEstado(estado) {
    switch (estado) {
        case 'equipaje_escaneado':
            return '#0d6efd'; // Azul
        case 'equipaje_cargado':
            return '#198754'; // Verde
        case 'equipaje_entregado':
            return '#fd7e14'; // Naranja
        case 'equipaje_perdido':
            return '#dc3545'; // Rojo
        default:
            return '#6c757d'; // Gris
    }
}

// Función para crear un mapa interactivo con Leaflet
function crearMapa(containerId, opciones = {}) {
    const defaultOpciones = {
        centro: [-34.6037, -58.3816], // Buenos Aires por defecto
        zoom: 4,
        maxZoom: 18,
        scrollWheelZoom: true
    };
    
    const config = { ...defaultOpciones, ...opciones };
    
    const mapa = L.map(containerId).setView(config.centro, config.zoom);
    
    // Añadir capa de tiles de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: config.maxZoom
    }).addTo(mapa);
    
    return mapa;
}

// Función para actualizar la fecha actual en la barra de navegación
function actualizarFechaActual() {
    const spanFecha = document.querySelector('.navbar .badge');
    if (spanFecha) {
        const fechaActual = new Date();
        const opciones = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        };
        spanFecha.innerHTML = `<i class="fas fa-calendar-day me-1"></i> ${fechaActual.toLocaleDateString('es-ES', opciones)}`;
    }
}

// Inicializar funciones cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar navegación activa
    actualizarNavActivo();
    
    // Actualizar fecha actual
    actualizarFechaActual();
    
    // Configurar modales
    const systemModal = document.getElementById('systemModal');
    if (systemModal) {
        const modal = new bootstrap.Modal(systemModal);
        
        // Exponer función global para mostrar modal del sistema
        window.mostrarModalSistema = function(titulo, mensaje) {
            document.getElementById('systemModalTitle').textContent = titulo;
            document.getElementById('systemModalBody').innerHTML = mensaje;
            modal.show();
        };
    }
    
    // Configurar formularios
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validarFormulario(form.id)) {
                e.preventDefault();
                mostrarNotificacion('Por favor, complete todos los campos requeridos.', 'warning');
            }
        });
    });
    
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

// Manejar errores AJAX globalmente
$(document).ajaxError(function(event, jqxhr, settings, thrownError) {
    console.error('Error AJAX:', thrownError);
    mostrarNotificacion('Error al cargar datos del servidor: ' + (jqxhr.statusText || 'Error desconocido'), 'danger');
});