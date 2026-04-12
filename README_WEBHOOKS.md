# Sistema de Webhooks Automáticos para Zulip

Este sistema implementa webhooks automáticos que generan resúmenes de conversaciones usando Ollama.

## Flujo de Trabajo

1. **Outgoing Webhook** (`xxx-bot`): Detecta cuando hay muchos mensajes no leídos en un topic
2. **Servicio Externo**: Recibe los mensajes, genera un resumen con Ollama
3. **Incoming Webhook** (`zzz-bot`): Publica el resumen en el stream/topic correspondiente

## Archivos del Sistema

- `outgoing_webhook.py` - Bot que detecta triggers y envía mensajes al servicio externo
- `webhook_service.py` - Servicio Flask que procesa mensajes y genera resúmenes con Ollama
- `incoming_webhook.py` - Bot que publica resúmenes en Zulip
- `setup_webhooks.py` - Configuración inicial del sistema
- `test_webhooks.py` - Pruebas completas del sistema
- `bot_config.json` - Configuración de los bots (actualizado con nuevas claves)

## Configuración

### 1. Configurar Bots en Zulip

Asegúrate de que los siguientes bots estén creados en tu organización Zulip:

- **xxx-bot** (Outgoing webhook): `xxx-bot@127.0.0.1.nip.io`
- **zzz-bot** (Incoming webhook): `zzz-bot@127.0.0.1.nip.io`

### 2. Instalar Dependencias

```bash
pip install flask requests
```

### 3. Configurar Ollama

Asegúrate de que Ollama esté corriendo en `http://localhost:11434` con el modelo `llama3`:

```bash
# Descargar modelo si no lo tienes
ollama pull llama3

# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags
```

## Instalación y Uso

### Paso 1: Configurar el Sistema

Ejecuta el script de configuración:

```bash
python setup_webhooks.py
```

Esto creará los streams necesarios y verificará las conexiones de los bots.

### Paso 2: Iniciar el Servicio de Webhooks

En una terminal, inicia el servicio Flask:

```bash
python webhook_service.py
```

El servicio correrá en `http://localhost:8080`

### Paso 3: Iniciar el Outgoing Webhook

En otra terminal, inicia el bot que detecta triggers:

```bash
python outgoing_webhook.py
```

Este bot monitoreará los streams configurados y detectará cuando hay 10+ mensajes no leídos.

### Paso 4: Probar el Sistema

Ejecuta las pruebas completas:

```bash
python test_webhooks.py
```

## Cómo Funciona

### Detección de Triggers

El sistema monitorea constantemente los streams/topics configurados. Cuando detecta:

- **10+ mensajes no leídos** en un topic
- **Mensajes recientes** en el stream

Activa el proceso de resumen.

### Generación de Resúmenes

1. Extrae el contenido de los mensajes recientes
2. Envía el contenido a Ollama con un prompt específico
3. Ollama genera un resumen en español (máximo 200 palabras)
4. El resumen incluye puntos clave, decisiones y acciones necesarias

### Publicación de Resúmenes

El resumen se publica automáticamente en:

- **Stream**: El mismo stream original
- **Topic**: `resumen-{topic-original}`

## Configuración Personalizada

### Cambiar Umbral de Mensajes

Edita `outgoing_webhook.py` y modifica la variable `threshold`:

```python
if self.check_unread_messages(stream, topic, threshold=15):  # Cambia 15 al valor deseado
```

### Cambiar Modelo de Ollama

Edita `webhook_service.py`:

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

## Monitoreo

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

## Solución de Problemas

### El servicio no responde

1. Verifica que Ollama esté corriendo: `curl http://localhost:11434/api/tags`
2. Verifica que el servicio Flask esté activo: `curl http://localhost:8080/health`
3. Revisa los logs de errores en las terminales

### Los bots no pueden conectarse a Zulip

1. Verifica las claves API en `bot_config.json`
2. Asegúrate de que los bots estén activos en Zulip
3. Ejecuta `python setup_webhooks.py` para verificar conexiones

### No se generan resúmenes

1. Verifica que haya suficientes mensajes no leídos (default: 10)
2. Revisa que Ollama esté funcionando correctamente
3. Envía mensajes de prueba con `python test_webhooks.py`

## Ejemplo de Flujo Completo

1. **Usuarios envían mensajes** en `#general/chat`
2. **Se acumulan 12 mensajes no leídos**
3. **xxx-bot detecta** el trigger y envía los mensajes al servicio
4. **Servicio procesa** los mensajes con Ollama y genera un resumen
5. **zzz-bot publica** el resumen en `#general/resumen-chat`

## Seguridad

- Los webhooks usan tokens de autenticación
- Las claves API están almacenadas en `bot_config.json`
- El servicio solo acepta requests del webhook configurado

## Personalización Avanzada

### Modificar Prompts de Resumen

Edita el prompt en `webhook_service.py` para cambiar cómo se generan los resúmenes.

### Agregar Más Tipos de Triggers

Puedes extender `outgoing_webhook.py` para detectar otros tipos de eventos:

- Palabras clave específicas
- Menciones a usuarios
- Cambios en el topic

## Soporte

Si tienes problemas:

1. Revisa los logs de cada componente
2. Ejecuta `python test_webhooks.py` para diagnóstico
3. Verifica que todos los servicios estén corriendo

---

**Nota**: Asegúrate de que todos los componentes estén corriendo simultáneamente para que el sistema funcione correctamente.
