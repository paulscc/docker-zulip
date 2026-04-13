# Zulip AI Features - Message Recap & Topic Title Improver

Este proyecto implementa dos funcionalidades principales de IA para Zulip:
1. **Message Recap**: Generación automática de resúmenes de mensajes no leídos con enlaces a los mensajes originales
2. **Topic Title Improver**: Detección automática de conversaciones desviadas y sugerencia de títulos actualizados para temas

## Arquitectura del Sistema

El sistema utiliza:
- **Zulip Server**: Plataforma de comunicación principal
- **Kafka**: Sistema de mensajería para procesamiento asíncrono
- **Python/Flask**: Backend para las funcionalidades de IA
- **Ollama/Gemini**: Modelos de lenguaje para generación de resúmenes y análisis de temas
- **Docker Compose**: Orquestación de contenedores

## Requisitos Previos

### Software Necesario
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+ (para desarrollo local)
- Ollama (opcional, para modelos locales)

### Hardware Recomendado
- RAM: 4GB mínimo, 8GB recomendado
- CPU: 2 núcleos mínimo, 4 núcleos recomendados
- Disco: 20GB espacio disponible

## Instalación

### 1. Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd <DIRECTORIO_DEL_PROYECTO>
```

### 2. Configurar Variables de Entorno
Crea un archivo `.env` con las siguientes variables:

```bash
# Configuración de Zulip
ZULIP_EMAIL=tu-bot@zulip.example.com
ZULIP_API_KEY=tu-api-key
ZULIP_SERVER=https://zulip.example.com

# Configuración de Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Configuración de IA
OLLAMA_URL=http://localhost:11434
GEMINI_API_KEY=tu-gemini-api-key
DEFAULT_LLM_MODEL=gemini-pro

# Configuración de Base de Datos
POSTGRES_PASSWORD=tu-secure-password
REDIS_PASSWORD=tu-redis-password
MEMCACHED_PASSWORD=tu-memcached-password
RABBITMQ_PASSWORD=tu-rabbitmq-password
SECRET_KEY=tu-secret-key
EMAIL_PASSWORD=tu-email-password
```

### 3. Iniciar los Servicios
```bash
# Generar secrets para Docker
echo "tu-postgres-password" > zulip-postgres-password
echo "tu-redis-password" > zulip-redis-password  
echo "tu-memcached-password" > zulip-memcached-password
echo "tu-rabbitmq-password" > zulip-rabbitmq-password
echo "tu-secret-key" > zulip-secret-key
echo "tu-email-password" > zulip-email-password

# Iniciar todos los servicios
docker-compose up -d
```

### 4. Instalar Dependencias de Python
```bash
pip install -r requirements.txt
pip install -r requirements_flask.txt
pip install -r requirements_kafka.txt
```

### 5. Configurar Ollama (opcional)
```bash
# Descargar modelo Gemma2
ollama pull gemma2

# Iniciar Ollama server
ollama serve
```

## Configuración de API Keys

### Para Gemini API
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API key
3. Agrégala a tu archivo `.env` como `GEMINI_API_KEY`

### Para Zulip Bot
1. En tu servidor Zulip, ve a Settings -> Bots
2. Crea un nuevo bot con tipo "Generic"
3. Copia el email y API key del bot
4. Agrégalos a tu archivo `.env`

## Uso

### Iniciar el Sistema Completo
```bash
# Iniciar Zulip y servicios relacionados
docker-compose up -d

# Iniciar backend de Flask
python app.py

# Iniciar bots de resumen
python summary_bot.py --zulip-email $ZULIP_EMAIL --zulip-api-key $ZULIP_API_KEY --zulip-server $ZULIP_SERVER

# Iniciar procesador de temas
python llm_topic_analyzer.py
```

### Acceder a la Interfaz Web
- **Frontend Principal**: http://localhost:5000
- **Zulip Server**: http://localhost (después de configuración inicial)

## Estructura del Proyecto

```
.
|-- app.py                          # Backend Flask principal
|-- summary_bot.py                  # Bot de notificación de resúmenes
|-- llm_topic_analyzer.py           # Analizador de temas con IA
|-- kafka_summary_processor.py      # Procesador de resúmenes Kafka
|-- templates/
|   |-- index.html                  # Frontend principal
|   `-- index1.html                 # Interfaz de monitoreo Kafka
|-- requirements*.txt               # Dependencias Python
|-- compose.yaml                    # Docker Compose configuration
|-- .env                            # Variables de entorno
|-- README.md                       # Este archivo
|-- implementation.md               # Documentación técnica
`-- ai.md                           # Uso de herramientas de IA
```

## Funcionalidades

### Message Recap
- Generación automática de resúmenes de mensajes no leídos
- Enlaces directos a mensajes originales
- Soporte para múltiples modelos de IA (Gemini, Gemma2)
- Configuración personalizable por usuario

### Topic Title Improver
- Detección de conversaciones desviadas (drifting discussions)
- Sugerencias automáticas de títulos actualizados
- Análisis de contexto y relevancia
- Integración con flujo de trabajo de Zulip

## Endpoints de API

### Message Recap
- `POST /api/recap/generate` - Generar resumen de mensajes
- `GET /api/recap/status/<user_id>` - Ver estado de resúmenes
- `POST /api/recap/preferences` - Configurar preferencias

### Topic Title Improver
- `POST /api/topics/analyze` - Analizar tema para sugerencias
- `GET /api/topics/status/<stream_id>` - Ver estado de análisis
- `POST /api/topics/update` - Actualizar título de tema

## Monitoreo y Logs

Los logs están disponibles en:
- **Logs de Flask**: Consola o archivo de logs configurado
- **Logs de Kafka**: Docker logs `docker-compose logs kafka`
- **Logs de Zulip**: Docker logs `docker-compose logs zulip`

## Solución de Problemas

### Issues Comunes
1. **Kafka no inicia**: Verificar que el puerto 9092 esté disponible
2. **Bot no responde**: Verificar API keys y configuración de red
3. **IA no responde**: Verificar conexión a Ollama o API key de Gemini

### Comandos Útiles
```bash
# Ver estado de los contenedores
docker-compose ps

# Reiniciar servicios específicos
docker-compose restart kafka zulip

# Ver logs en tiempo real
docker-compose logs -f kafka
```

## Contribución

1. Fork del repositorio
2. Crear feature branch
3. Commit de cambios
4. Push al branch
5. Crear Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear issue en el repositorio
- Contactar al equipo del proyecto
- Revisar documentación adicional en `/docs`
