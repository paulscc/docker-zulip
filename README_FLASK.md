# Kafka Messages Viewer - Flask Web Application

Una aplicación web simple construida con Flask que consume mensajes de Kafka y los muestra en tiempo real en una interfaz web.

## Características

- **Consumo de Kafka**: Conecta a un broker de Kafka y consume mensajes de los tópicos `zulip-unread-messages` y `zulip-summaries`
- **Interfaz Web Moderna**: Diseño responsivo con actualización automática cada 3 segundos
- **Estadísticas en Tiempo Real**: Muestra total de mensajes y mensajes por minuto
- **Indicador de Conexión**: Visualización del estado de conexión con Kafka
- **Formato JSON**: Muestra los mensajes en formato JSON legible

## Requisitos Previos

1. **Python 3.7+**
2. **Kafka Broker** corriendo en `localhost:9092`
3. **Tópicos Kafka** llamados `zulip-unread-messages` y `zulip-summaries`

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements_flask.txt
```

2. Asegurarse que Kafka está corriendo y el tópico existe:
```bash
# Crear los tópicos si no existen
kafka-topics.sh --create --topic zulip-unread-messages --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic zulip-summaries --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

## Ejecución

1. Iniciar la aplicación Flask:
```bash
python flask_app.py
```

2. Abrir el navegador en: `http://localhost:5000`

## Configuración

### Configuración de Kafka
Puedes modificar la configuración de Kafka en `flask_app.py`:

```python
self.consumer = KafkaConsumer(
    'zulip-unread-messages',  # Tópico para mensajes no leídos
    'zulip-summaries',       # Tópico para resúmenes
    bootstrap_servers=['localhost:9092'],  # Cambiar broker/servers
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='flask_web_group'
)
```

### Configuración del Servidor Flask
En la parte inferior de `flask_app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## API Endpoints

- `GET /` - Página principal con la interfaz web
- `GET /api/messages` - Retorna los mensajes más recientes en formato JSON
- `GET /api/health` - Estado de salud de la aplicación y conexión Kafka

## Estructura del Proyecto

```
.
|-- flask_app.py              # Aplicación Flask principal
|-- templates/
|   `-- index.html          # Template HTML para la interfaz
|-- requirements_flask.txt   # Dependencias Python
`-- README_FLASK.md         # Este archivo
```

## Funcionalidades de la Interfaz

- **Auto Refresh**: Actualización automática cada 3 segundos (se puede desactivar)
- **Manual Refresh**: Botón para actualizar manualmente los mensajes
- **Clear**: Botón para limpiar la vista y recargar
- **Estadísticas**: Muestra total de mensajes y tasa por minuto
- **Estado de Conexión**: Indicador visual de la conexión con Kafka

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a Kafka**:
   - Verificar que Kafka está corriendo: `kafka-topics.sh --list --bootstrap-server localhost:9092`
   - Verificar que el tópico existe
   - Revisar la configuración del broker

2. **Error de importación**:
   - Asegurarse de instalar todas las dependencias: `pip install -r requirements_flask.txt`

3. **Puerto en uso**:
   - Cambiar el puerto en `app.run(host='0.0.0.0', port=5000)`

## Mejoras Futuras

- Integración con WebSocket para actualizaciones en tiempo real
- Persistencia de mensajes en base de datos
- Autenticación de usuarios
- Filtrado y búsqueda de mensajes
- Configuración dinámica de tópicos Kafka
