# Scripts para Sistema de Enlaces en Mensajes Kafka

## Scripts Principales

### 1. **outgoing_webhook.py** - Webhook de Salida con Enlaces
**Propósito**: Detecta mensajes no leídos y los envía a Kafka con enlaces directos

```bash
# Ejecutar en segundo plano
python outgoing_webhook.py
```

**Funciones clave**:
- `get_recent_messages()`: Obtiene mensajes y agrega enlaces directos
- `send_to_kafka()`: Envía mensajes con enlaces a topic `zulip-unread-messages`
- `monitor_streams()`: Monitorea streams configurados

### 2. **webhook_service_kafka.py** - Servicio Web con Kafka
**Propósito**: Servicio Flask que maneja endpoints para Kafka

```bash
# Ejecutar en segundo plano
python webhook_service_kafka.py
```

**Endpoints**:
- `POST /kafka/send-unread`: Envía mensajes directamente a Kafka
- `GET /health`: Verifica estado del servicio

### 3. **kafka_summary_processor.py** - Procesador de Resúmenes
**Propósito**: Consume mensajes de `zulip-unread-messages` y genera resúmenes

```bash
# Ejecutar en segundo plano
python kafka_summary_processor.py
```

### 4. **incoming_webhook.py** - Webhook de Entrada
**Propósito**: Consume resúmenes de `zulip-summaries` y los publica en Zulip

```bash
# Ejecutar en segundo plano
python incoming_webhook.py
```

## Scripts de Prueba

### 5. **test_links_direct.py** - Prueba de Enlaces Directos
**Propósito**: Envía mensajes de prueba con enlaces a Kafka

```bash
# Ejecutar prueba
python test_links_direct.py
```

**Función**: Verifica que los mensajes se envíen con enlaces directos correctamente

### 6. **send_kafka_test.py** - Prueba Básica de Kafka
**Propósito**: Envía mensajes simples a Kafka

```bash
# Ejecutar prueba
python send_kafka_test.py
```

### 7. **test_messages_with_links.py** - Verificación de Enlaces
**Propósito**: Verifica que los mensajes en Kafka contengan enlaces

```bash
# Ejecutar verificación
python test_messages_with_links.py
```

## Scripts de Configuración

### 8. **setup_kafka_topics.py** - Configuración de Topics
**Propósito**: Crea los topics necesarios en Kafka

```bash
# Configurar topics
python setup_kafka_topics.py
```

### 9. **demo_webhook_kafka.py** - Demostración Completa
**Propósito**: Envía mensajes a Zulip para probar el flujo completo

```bash
# Ejecutar demo
python demo_webhook_kafka.py
```

## Flujo de Ejecución Completo

### Para producción:

```bash
# Terminal 1: Servicio Web
python webhook_service_kafka.py

# Terminal 2: Webhook de Salida
python outgoing_webhook.py

# Terminal 3: Procesador de Resúmenes
python kafka_summary_processor.py

# Terminal 4: Webhook de Entrada
python incoming_webhook.py
```

### Para pruebas:

```bash
# Prueba básica de enlaces
python test_links_direct.py

# Verificar mensajes en Kafka
docker exec opcion2-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic zulip-unread-messages --from-beginning --timeout-ms 5000

# Verificar resúmenes
docker exec opcion2-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic zulip-summaries --from-beginning --timeout-ms 5000
```

## Scripts de Mantenimiento

### 10. **backup_kafka_data.sh** - Backup de Datos Kafka
**Propósito**: Crear backup de los datos de Kafka

```bash
# Crear backup
docker run --rm -v opcion2_kafka:/data -v backup:/backup alpine tar czf /backup/kafka_backup_$(date +%Y%m%d).tar.gz -C /data .
```

### 11. **restore_kafka_data.sh** - Restauración de Datos
**Propósito**: Restaurar datos de Kafka desde backup

```bash
# Restaurar backup
docker run --rm -v opcion2_kafka:/data -v backup:/backup alpine tar xzf /backup/kafka_backup.tar.gz -C /data
```

## Archivos de Configuración

### **bot_config.json**
Configuración de bots y canales monitoreados

### **compose.yaml**
Configuración de contenedores Docker

### **requirements.txt** y **requirements_kafka.txt**
Dependencias Python necesarias

## Resumen de Scripts Esenciales

| Script | Propósito | Modo de uso |
|--------|-----------|--------------|
| `outgoing_webhook.py` | Principal - agrega enlaces | Producción |
| `webhook_service_kafka.py` | Servicio web | Producción |
| `kafka_summary_processor.py` | Procesamiento | Producción |
| `incoming_webhook.py` | Publicación en Zulip | Producción |
| `test_links_direct.py` | Prueba de enlaces | Desarrollo |
| `send_kafka_test.py` | Prueba básica | Desarrollo |

## Comandos útiles

```bash
# Verificar estado de Kafka
docker exec opcion2-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list

# Verificar mensajes en topic
docker exec opcion2-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic zulip-unread-messages --from-beginning --timeout-ms 5000

# Reiniciar Kafka si es necesario
docker restart opcion2-kafka-1

# Verificar logs
docker logs opcion2-kafka-1 --tail 20
```

Estos scripts cubren todo el flujo desde la detección de mensajes hasta la publicación de resúmenes con enlaces directos a cada mensaje.
