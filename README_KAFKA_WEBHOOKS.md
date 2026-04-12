# Sistema de Webhooks Automáticos con Kafka para Zulip

Este sistema implementa webhooks automáticos que generan resúmenes de conversaciones usando Ollama y Kafka como intermediario.

## Nuevo Flujo de Trabajo con Kafka

1. **Outgoing Webhook** (`xxx-bot`): Detecta mensajes no leídos y los envía al topic Kafka `zulip-unread-messages`
2. **Kafka Processor**: Consume mensajes del topic `zulip-unread-messages`, genera resúmenes con Ollama
3. **Kafka Producer**: Publica resúmenes en el topic Kafka `zulip-summaries`
4. **Incoming Webhook** (`zzz-bot`): Consume resúmenes del topic `zulip-summaries` y los publica en Zulip

## Arquitectura del Sistema

```
Zulip (Stream/Topic) 
    |
    v
Outgoing Webhook (xxx-bot)
    |
    v
Kafka Topic: zulip-unread-messages
    |
    v
Kafka Summary Processor (con Ollama)
    |
    v
Kafka Topic: zulip-summaries
    |
    v
Incoming Webhook (zzz-bot)
    |
    v
Zulip (Stream/resumen-topic)
```

## Archivos del Sistema con Kafka

### Scripts Principales
- `outgoing_webhook.py` - Bot que detecta triggers y envía mensajes a Kafka
- `kafka_summary_processor.py` - Consume mensajes de Kafka y genera resúmenes con Ollama
- `incoming_webhook.py` - Consume resúmenes de Kafka y publica en Zulip

### Configuración y Pruebas
- `setup_kafka_topics.py` - Configura los topics de Kafka necesarios
- `webhook_service_kafka.py` - Servicio Flask alternativo con soporte Kafka
- `test_kafka_webhooks.py` - Pruebas completas del sistema Kafka

### Configuración
- `bot_config.json` - Configuración de los bots (actualizado con nuevas claves)

## Configuración de Kafka

### Topics de Kafka
- **zulip-unread-messages**: Recibe mensajes no leídos desde Zulip
- **zulip-summaries**: Contiene los resúmenes generados por Ollama

### Instalación y Configuración

#### 1. Configurar Topics de Kafka

```bash
python setup_kafka_topics.py
```

Esto creará los topics necesarios en Kafka.

#### 2. Instalar Dependencias

```bash
pip install flask requests
```

#### 3. Configurar Ollama

Asegúrate de que Ollama esté corriendo:

```bash
# Descargar modelo si no lo tienes
ollama pull llama3

# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags
```

## Modos de Operación

### Modo 1: Sistema Completo con Scripts Independientes

**Terminal 1 - Processor de Kafka:**
```bash
python kafka_summary_processor.py
```

**Terminal 2 - Outgoing Webhook:**
```bash
python outgoing_webhook.py
```

**Terminal 3 - Incoming Webhook:**
```bash
python incoming_webhook.py
```

### Modo 2: con Servicio Flask (Alternativo)

**Terminal 1 - Servicio Flask con Kafka:**
```bash
python webhook_service_kafka.py
```

**Terminal 2 - Outgoing Webhook:**
```bash
python outgoing_webhook.py
```

**Terminal 3 - Incoming Webhook:**
```bash
python incoming_webhook.py
```

## Flujo de Trabajo Detallado

### 1. Detección de Triggers
- El outgoing webhook monitorea streams/topics configurados
- Detecta cuando hay 10+ mensajes no leídos
- Extrae los mensajes recientes del stream/topic

### 2. Envío a Kafka
- Formatea los mensajes en JSON
- Publica en el topic `zulip-unread-messages`
- Incluye metadata: stream, topic, timestamp, webhook_token

### 3. Procesamiento en Kafka
- El processor consume mensajes de `zulip-unread-messages`
- Extrae el contenido de los mensajes
- Envía el contenido a Ollama para generar resúmenes

### 4. Generación de Resúmenes
- Ollama procesa los mensajes con un prompt específico
- Genera resúmenes en español (máximo 200 palabras)
- Identifica puntos clave, decisiones y acciones necesarias

### 5. Publicación de Resúmenes
- El processor publica resúmenes en `zulip-summaries`
- El incoming webhook consume los resúmenes
- Publica en Zulip: `stream/resumen-{topic-original}`

## Pruebas del Sistema

### Ejecutar Pruebas Completas

```bash
python test_kafka_webhooks.py
```

Esto verificará:
- Conexión a Kafka
- Existencia de topics requeridos
- Conexión de bots a Zulip
- Funcionamiento del servicio Flask
- Flujo completo de mensajes

### Pruebas Manuales

#### Verificar Topics de Kafka
```bash
docker exec opcion2-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
```

#### Verificar Mensajes en Topics
```bash
# Mensajes no leídos
docker exec opcion2-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic zulip-unread-messages --from-beginning --timeout-ms 5000

# Resúmenes
docker exec opcion2-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic zulip-summaries --from-beginning --timeout-ms 5000
```

## Configuración Personalizada

### Cambiar Umbral de Mensajes

Edita `outgoing_webhook.py`:
```python
if self.check_unread_messages(stream, topic, threshold=15):  # Cambia 15 al valor deseado
```

### Cambiar Modelo de Ollama

Edita `kafka_summary_processor.py`:
```python
self.ollama_model = "gemma3:1b"  # Cambia al modelo que prefieras
```

### Agregar Nuevos Streams

Edita `bot_config.json` y agrega nuevos canales a los bots de webhook:
```json
{
  "stream": "nuevo-stream",
  "topic": "topic-general"
}
```

### Cambiar Nombres de Topics de Kafka

Edita los archivos principales:
```python
self.kafka_topic_unread = "mi-topic-unread"
self.kafka_topic_summaries = "mi-topic-summaries"
```

## Monitoreo y Diagnóstico

### Verificar Estado del Servicio

```bash
curl http://localhost:8080/status
```

### Health Check

```bash
curl http://localhost:8080/health
```

### Logs del Sistema

Los logs se muestran en tiempo real en las terminales donde corren los scripts.

### Verificar Consumo de Kafka

Los scripts mostrarán logs cuando consuman mensajes de los topics.

## Solución de Problemas

### Kafka no responde

1. Verifica que el contenedor Kafka esté corriendo:
   ```bash
   docker ps | grep kafka
   ```

2. Verifica los topics:
   ```bash
   python setup_kafka_topics.py
   ```

### No se consumen mensajes de Kafka

1. Verifica que los consumers estén corriendo
2. Revisa los logs de los scripts
3. Verifica que haya mensajes en los topics

### Los resúmenes no se publican en Zulip

1. Verifica la conexión del incoming webhook
2. Revisa los logs del consumidor de resúmenes
3. Verifica que Ollama esté funcionando

### Mensajes no llegan a Kafka

1. Verifica la conexión del outgoing webhook
2. Revisa los logs del productor
3. Verifica que el topic `zulip-unread-messages` exista

## Ventajas del Sistema con Kafka

### 1. Desacoplamiento
- Los componentes pueden operar independientemente
- Mayor tolerancia a fallos
- Escalabilidad horizontal

### 2. Persistencia
- Los mensajes se guardan en Kafka
- Recuperación ante fallos
- Replay de mensajes si es necesario

### 3. Escalabilidad
- Múltiples consumers pueden procesar mensajes
- Balanceo de carga automático
- Procesamiento paralelo

### 4. Monitoreo
- Visibilidad completa del flujo de mensajes
- Métricas de consumo y producción
- Diagnóstico fácil de problemas

## Ejemplo de Flujo Completo con Kafka

1. **Usuarios envían 12 mensajes** en `#general/chat`
2. **xxx-bot detecta** el trigger y publica en `zulip-unread-messages`
3. **kafka_summary_processor** consume los mensajes y los envía a Ollama
4. **Ollama genera** un resumen conciso en español
5. **Processor publica** el resumen en `zulip-summaries`
6. **zzz-bot consume** el resumen y publica en `#general/resumen-chat`

## Seguridad

- Los webhooks usan tokens de autenticación
- Las claves API están almacenadas en `bot_config.json`
- Kafka topics están configurados con replicas y particiones
- Validación de mensajes en todos los componentes

## Rendimiento y Optimización

### Configuración de Topics
- 3 particiones por topic para paralelismo
- Replicación factor 1 (puede aumentarse)
- Configuración de retención según necesidades

### Optimización de Ollama
- Temperatura ajustada para resúmenes consistentes
- Límite de tokens para respuestas concisas
- Timeout configurado para evitar bloqueos

---

**Nota**: Asegúrate de que todos los componentes estén corriendo simultáneamente para que el sistema funcione correctamente con Kafka.
