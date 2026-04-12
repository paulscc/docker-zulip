# Sistema de Resúmenes Automáticos de Mensajes Zulip

## Overview

Sistema completo para generar resúmenes automáticos de mensajes no leídos en Zulip utilizando Kafka como middleware y Gemini API para procesamiento de IA.

## Arquitectura

```
Zulip Messages -> Kafka Producer -> Kafka Topics -> Consumer (Gemini) -> Summary Bot -> Users
```

### Componentes

1. **Kafka Producer** (`kafka_summary_producer.py`)
   - Captura mensajes nuevos de Zulip
   - Publica a topics de Kafka
   - Dispara resúmenes por tiempo y volumen

2. **Kafka Consumer** (`kafka_summary_consumer.py`)
   - Procesa triggers de resumen
   - Usa Gemini API para resúmenes grandes (>5 mensajes)
   - Usa Ollama local para resúmenes pequeños
   - Envía resultados a topic de resúmenes

3. **Summary Bot** (`summary_bot.py`)
   - Recibe resúmenes generados
   - Envía notificaciones a usuarios
   - Gestiona preferencias de usuario

## Configuración

### Variables de Entorno

```bash
# En tu archivo .env
gemikey=tu_gemini_api_key_aqui
SUMMARY_BOT_EMAIL=summary-bot@yourdomain.com
SUMMARY_BOT_API_KEY=tu_bot_api_key
ZULIP_SERVER_URL=https://your-zulip-server.com
OLLAMA_URL=http://localhost:11434
USE_OLLAMA=true
```

### Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements_kafka.txt
```

2. **Configurar Kafka:**
```bash
# Iniciar Kafka con el compose actualizado
docker-compose up -d kafka zookeeper
```

3. **Crear topics de Kafka:**
```bash
docker exec -it kafka kafka-topics --create --topic unread_messages --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it kafka kafka-topics --create --topic message_events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it kafka kafka-topics --create --topic summary_triggers --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it kafka kafka-topics --create --topic summary_results --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

## Uso

### Iniciar Sistema Completo

```bash
# 1. Iniciar servicios Kafka
docker-compose up -d kafka zookeeper

# 2. Iniciar Producer (captura mensajes)
python kafka_summary_producer.py \
    --zulip-email summary-bot@yourdomain.com \
    --zulip-api-key YOUR_API_KEY \
    --zulip-server https://your-zulip-server.com \
    --kafka-servers localhost:9092

# 3. Iniciar Consumer (procesamiento con IA)
python kafka_summary_consumer.py --kafka-servers localhost:9092

# 4. Iniciar Bot de notificaciones
python summary_bot.py \
    --zulip-email summary-bot@yourdomain.com \
    --zulip-api-key YOUR_API_KEY \
    --zulip-server https://your-zulip-server.com \
    --kafka-servers localhost:9092
```

### Usar Docker Compose para Servicios de Resumen

```bash
# Configurar variables de entorno
export SUMMARY_BOT_EMAIL="summary-bot@yourdomain.com"
export SUMMARY_BOT_API_KEY="YOUR_API_KEY"
export ZULIP_SERVER_URL="https://your-zulip-server.com"

# Iniciar servicios de resumen
docker-compose -f docker-compose-summary.yaml up -d
```

## Configuración de Resúmenes

### Disparadores Automáticos

1. **Por Volumen:** Se activa cuando hay 10+ mensajes en un stream/topic
2. **Por Tiempo:** Se activa cada 5 minutos con mensajes pendientes
3. **Híbrido:** Combinación de ambos métodos

### Tipos de Resumen

- **Gemini API:** Para >5 mensajes (resúmenes detallados)
- **Ollama Local:** Para <=5 mensajes (resúmenes simples)
- **Simple:** Fallback sin IA

### Preferencias de Usuario

```python
# Ejemplo de configuración por usuario
user_preferences = {
    'summary_interval': 'both',  # 'time', 'count', 'both'
    'min_messages': 5,
    'max_messages': 50,
    'streams': ['general', 'desarrollo'],  # Streams específicos
    'notification_type': 'private'  # 'private' o 'stream'
}
```

## Topics de Kafka

- **unread_messages:** Todos los mensajes nuevos
- **message_events:** Eventos de mensajes
- **summary_triggers:** Disparadores de resumen
- **summary_results:** Resúmenes generados

## Monitoreo

### Logs

Cada componente genera logs detallados:

```bash
# Ver logs de servicios
docker-compose logs -f summary-producer
docker-compose logs -f summary-consumer
docker-compose logs -f summary-bot
```

### Métricas

- Número de mensajes procesados
- Resúmenes generados por tipo
- Tiempo de procesamiento
- Errores de API

## Troubleshooting

### Problemas Comunes

1. **Kafka no conecta:**
```bash
# Verificar estado de Kafka
docker exec -it kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

2. **API Gemini falla:**
- Verificar que `gemikey` esté configurada
- Revisar cuotas de API

3. **Bot no envía mensajes:**
- Verificar permisos del bot en Zulip
- Revisar configuración de streams

### Debug

```bash
# Ver topics de Kafka
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Ver mensajes en un topic
docker exec -it kafka kafka-console-consumer --topic unread_messages --bootstrap-server localhost:9092 --from-beginning
```

## Personalización

### Modificar Umbrales

En `kafka_summary_producer.py`:
```python
# Cambiar umbral de mensajes
if len(self.message_buffer[stream_topic]) >= 10:  # Cambiar este valor
```

### Modificar Intervalo de Tiempo

En `kafka_summary_producer.py`:
```python
# Cambiar intervalo de 5 minutos
if (current_time - self.last_check_time).total_seconds() >= 300:  # Cambiar 300
```

### Personalizar Prompt de Gemini

En `kafka_summary_consumer.py` modificar el método `_generate_gemini_summary()`.

## Seguridad

- API keys almacenadas como secrets de Docker
- Conexiones SSL verificadas cuando es posible
- Aislamiento de contenedores
- Logs sin información sensible

## Escalabilidad

- Kafka permite múltiples consumers
- Particiones por stream/topic
- Procesamiento paralelo
- Persistencia de mensajes

## Costos

- **Gemini API:** ~$0.00025 por 1K tokens (resúmenes grandes)
- **Ollama:** Gratis (local)
- **Kafka:** Recursos de infraestructura
- **Zulip:** Ya existente

## Roadmap Futuro

1. Dashboard web de configuración
2. Integración con más LLMs
3. Resúmenes personalizados por rol
4. Análisis de sentimiento
5. Búsqueda en resúmenes históricos
