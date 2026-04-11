# Zulip Multi-Bot Framework

Un framework completo para crear y gestionar múltiples bots de chat en Zulip.

## Características

- **Múltiples Bots**: Configura y ejecuta tantos bots como necesites
- **Personalidades**: Cada bot puede tener una personalidad diferente (friendly, technical, casual, professional)
- **Canales Específicos**: Configura en qué canales hablará cada bot
- **Mensajes Automáticos**: Los bots envían mensajes automáticamente a intervalos configurables
- **Control Total**: Inicia, detén y envía mensajes manualmente desde cualquier bot

## Instalación

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Iniciar Zulip** (si no está corriendo):
```bash
docker compose up -d
```

## Configuración

### 1. Crear los Bots en Zulip

1. Accede a tu servidor Zulip en http://localhost:9991
2. Inicia sesión como administrador
3. Ve a "Settings" (engranaje) > "Add bots and integrations"
4. Click en "Add a new bot"
5. Tipo: "Generic bot"
6. Usa los nombres y emails del archivo `bot_config.json`
7. Click en "Create bot"

### 2. Obtener API Keys

Para cada bot creado:
1. Descarga el archivo .zuliprc del bot
2. Copia el API key del archivo .zuliprc
3. Actualiza el API key en `bot_config.json`

### 3. Crear Canales

Crea los siguientes canales en Zulip:
- `general`
- `social`
- `tecnico`
- `desarrollo`
- `random`
- `proyectos`
- `anuncios`

## Uso

### Comandos Básicos

```bash
# Listar todos los bots configurados
python zulip_bots_framework.py --action list

# Iniciar todos los bots
python zulip_bots_framework.py --action start-all

# Iniciar un bot específico
python zulip_bots_framework.py --action start --bot bot_amigable

# Detener todos los bots
python zulip_bots_framework.py --action stop-all

# Detener un bot específico
python zulip_bots_framework.py --action stop --bot bot_amigable

# Enviar mensaje manual desde un bot
python zulip_bots_framework.py --action message --bot bot_amigable --stream general --topic chat --message "Hola mundo!"
```

### Configuración de Bots

Edita `bot_config.json` para personalizar tus bots:

```json
{
  "bots": [
    {
      "bot_name": "bot_amigable",
      "email": "bot_amigable@localhost",
      "api_key": "YOUR_API_KEY_HERE",
      "server_url": "http://localhost:9991",
      "personality": "friendly",
      "channels": [
        {"stream": "general", "topic": "chat"},
        {"stream": "social", "topic": "conversacion"}
      ],
      "message_interval": 300
    }
  ]
}
```

### Personalidades Disponibles

- **friendly**: Mensajes amigables y sociales
- **technical**: Mensajes técnicos y de soporte
- **casual**: Mensajes informales y de entretenimiento
- **professional**: Mensajes profesionales y formales

### Configuración de Canales

Cada bot puede estar configurado para múltiples canales:

```json
"channels": [
  {"stream": "nombre_canal", "topic": "nombre_topic"},
  {"stream": "otro_canal", "topic": "general"}
]
```

### Intervalos de Mensaje

Configura cada cuánto tiempo enviará mensajes el bot (en segundos):

```json
"message_interval": 300  // 5 minutos
```

## Ejemplos de Uso

### Escenario 1: Bot de Bienvenida
```json
{
  "bot_name": "bot_bienvenida",
  "personality": "friendly",
  "channels": [{"stream": "general", "topic": "bienvenida"}],
  "message_interval": 600
}
```

### Escenario 2: Bot de Soporte Técnico
```json
{
  "bot_name": "bot_soporte",
  "personality": "technical", 
  "channels": [
    {"stream": "soporte", "topic": "ayuda"},
    {"stream": "tecnico", "topic": "issues"}
  ],
  "message_interval": 180
}
```

### Escenario 3: Bot de Anuncios
```json
{
  "bot_name": "bot_anuncios",
  "personality": "professional",
  "channels": [{"stream": "anuncios", "topic": "general"}],
  "message_interval": 3600
}
```

## Archivos del Proyecto

- `zulip_bots_framework.py`: Framework principal
- `bot_config.json`: Configuración de bots
- `setup_bots.py`: Script de configuración inicial
- `requirements.txt`: Dependencias Python
- `README_BOTS.md`: Esta documentación

## Troubleshooting

### Error de Conexión
Si recibes errores de conexión, verifica:
1. Que Zulip esté corriendo (`docker compose ps`)
2. Que el server_url sea correcto (`http://localhost:9991`)
3. Que los API keys sean válidos

### Bots No Inician
Verifica:
1. Que los bots existan en Zulip
2. Que los API keys sean correctos
3. Que los canales existan en Zulip

### Mensajes No Se Envían
Revisa:
1. Que el bot tenga permisos en el canal
2. Que el stream y topic existan
3. Que el bot esté suscrito al stream

## Personalización Avanzada

### Agregar Nueva Personalidad

Edita `zulip_bots_framework.py` en el método `generate_message()`:

```python
messages = {
  'friendly': [...],
  'technical': [...],
  'mi_personalidad': [
    "Mensaje personalizado 1",
    "Mensaje personalizado 2"
  ]
}
```

### Mensajes Contextuales

Puedes extender el framework para generar mensajes basados en contexto:

```python
def generate_message(self, context: Dict[str, Any] = None) -> str:
    if context and 'time_of_day' in context:
        # Mensajes basados en hora del día
        pass
    # Lógica personalizada
```

## Seguridad

- Mantén los API keys seguros
- No compartas el archivo `bot_config.json` con credenciales reales
- Considera usar variables de entorno para producción

## Contribuciones

Siéntete libre de extender el framework con:
- Nuevas personalidades
- Integraciones con APIs externas
- Respuestas inteligentes con IA
- Sistema de plugins

## Licencia

Este framework es open source. Siéntete libre de usarlo y modificarlo según tus necesidades.
