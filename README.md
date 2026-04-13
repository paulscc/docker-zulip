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

#### Opción A: Configuración Automática (Recomendada)

Usa el script automático para configurar todos los bots:

```bash
python setup_bot_keys.py
```

El script te guiará paso a paso para:
- Crear las API keys en Zulip
- Configurar los 4 bots principales
- Generar el archivo `.env` automáticamente

#### Opción B: Configuración Manual

Copia la plantilla y edita manualmente:

```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

**Variables principales requeridas:**

```bash
# Bots de Zulip (4 bots principales)
SUMMARY_BOT_EMAIL=summary-bot@tu-servidor.zulipchat.com
SUMMARY_BOT_API_KEY=tu-api-key-aqui
SUMMARY_BOT_SERVER=https://tu-servidor.zulipchat.com

TOPIC_ANALYZER_BOT_EMAIL=topic-analyzer-bot@tu-servidor.zulipchat.com
TOPIC_ANALYZER_BOT_API_KEY=tu-api-key-aqui
TOPIC_ANALYZER_BOT_SERVER=https://tu-servidor.zulipchat.com

FOCUS_BOT_EMAIL=focus-monitor-bot@tu-servidor.zulipchat.com
FOCUS_BOT_API_KEY=tu-api-key-aqui
FOCUS_BOT_SERVER=https://tu-servidor.zulipchat.com

WEBHOOK_BOT_EMAIL=webhook-bot@tu-servidor.zulipchat.com
WEBHOOK_BOT_API_KEY=tu-api-key-aqui
WEBHOOK_BOT_SERVER=https://tu-servidor.zulipchat.com

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

### Configuración Automática con Script

Ejecuta el script para configuración guiada:

```bash
python setup_bot_keys.py
```

El script creará automáticamente el archivo `BOT_CREATION_INSTRUCTIONS.md` con instrucciones detalladas.

### Configuración Manual

#### Para Gemini API
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API key
3. Agrégala a tu archivo `.env` como `GEMINI_API_KEY`

#### Para Zulip Bots (4 bots requeridos)

**1. Bot de Resúmenes (Summary Bot)**
- Tipo: Generic bot
- Email: summary-bot@tu-servidor.zulipchat.com
- Función: Generar y enviar resúmenes de mensajes

**2. Bot de Análisis de Tópicos (Topic Analyzer Bot)**
- Tipo: Generic bot
- Email: topic-analyzer-bot@tu-servidor.zulipchat.com
- Función: Analizar conversaciones y sugerir títulos

**3. Bot de Monitoreo de Enfoque (Focus Monitor Bot)**
- Tipo: Generic bot
- Email: focus-monitor-bot@tu-servidor.zulipchat.com
- Función: Monitorear enfoque de conversaciones

**4. Bot de Webhook (Webhook Bot)**
- Tipo: Generic bot
- Email: webhook-bot@tu-servidor.zulipchat.com
- Función: Recibir y procesar webhooks

**Pasos para crear cada bot:**
1. En tu servidor Zulip, ve a Settings -> Bots -> Add a new bot
2. Selecciona "Generic bot"
3. Ingresa el nombre y email correspondiente
4. Crea el bot y copia la API key generada
5. Agrégala a tu archivo `.env`

**Permisos requeridos para todos los bots:**
- Acceso a los streams relevantes
- Capacidad de leer mensajes
- Capacidad de enviar mensajes
- Acceso a la API de Zulip

## Uso

### Iniciar el Sistema Completo

#### Método 1: Usando variables de entorno (.env)
```bash
# Iniciar Zulip y servicios relacionados
docker-compose up -d

# Iniciar backend de Flask
python app.py

# Iniciar bots (usará configuración del .env)
python summary_bot.py
python kafka_summary_processor.py
python llm_topic_analyzer.py
python focus_webhook.py
python incoming_webhook.py
```

#### Método 2: Pasando parámetros manualmente
```bash
# Iniciar Zulip y servicios relacionados
docker-compose up -d

# Iniciar backend de Flask
python app.py

# Iniciar bots específicos con parámetros
python summary_bot.py --zulip-email $SUMMARY_BOT_EMAIL --zulip-api-key $SUMMARY_BOT_API_KEY --zulip-server $SUMMARY_BOT_SERVER
python llm_topic_analyzer.py --zulip-email $TOPIC_ANALYZER_BOT_EMAIL --zulip-api-key $TOPIC_ANALYZER_BOT_API_KEY --zulip-server $TOPIC_ANALYZER_BOT_SERVER
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
|-- focus_webhook.py                # Webhook de monitoreo de enfoque
|-- incoming_webhook.py             # Webhook entrante
|-- contextual_focus_analyzer.py    # Analizador de contexto
|-- setup_bot_keys.py               # Script de configuración automática
|-- templates/
|   |-- index.html                  # Frontend principal
|   |-- index1.html                 # Interfaz de monitoreo Kafka
|   |-- topic_improver.html         # Interfaz de mejora de tópicos
|   `-- message_recap.html          # Interfaz de resúmenes
|-- requirements*.txt               # Dependencias Python
|-- .env.example                    # Plantilla de configuración
|-- .env                            # Variables de entorno (crear desde .env.example)
|-- compose.yaml                    # Docker Compose configuration
|-- README.md                       # Este archivo
|-- implementation.md               # Documentación técnica
|-- ai.md                           # Uso de herramientas de IA
`-- BOT_CREATION_INSTRUCTIONS.md   # Instrucciones para crear bots (generado por script)
```

## Funcionalidades

### Message Recap
- Generación automática de resúmenes de mensajes no leídos
- Enlaces directos a mensajes originales
- Soporte para múltiples modelos de IA (Gemini, Gemma2)
- Configuración personalizable por usuario
- Procesamiento asíncrono con Kafka

### Topic Title Improver
- Detección de conversaciones desviadas (drifting discussions)
- Sugerencias automáticas de títulos actualizados
- Análisis de contexto y relevancia
- Integración con flujo de trabajo de Zulip

### Focus Monitoring
- Monitoreo de enfoque en tiempo real
- Análisis contextual de conversaciones
- Detección de temas relevantes
- Notificaciones automáticas

### Webhook Integration
- Recepción de webhooks externos
- Procesamiento de eventos en tiempo real
- Integración con sistemas third-party
- Enrutamiento inteligente de mensajes

### Automated Bot Management
- Configuración automática de 4 bots especializados
- Script de setup guiado
- Gestión centralizada de API keys
- Plantillas reutilizables

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
