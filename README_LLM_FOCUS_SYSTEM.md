# Sistema de Monitoreo de Conversación con LLM

## Descripción

Sistema completo que vigila el canal `desarrollo` (tecnología) en Zulip y mantiene el foco en la conversación original usando análisis con LLM (Gemma2).

## Componentes

### 1. LLM Conversation Analyzer (`llm_conversation_analyzer.py`)
- Analiza conversaciones cada 20 segundos
- Usa Gemma2 para detectar cambios de tema
- Envía recordatorios de foco vía webhook

### 2. Incoming Focus Webhook (`incoming_focus_webhook.py`)
- Recibe mensajes del analyzer
- Envía recordatorios a Zulip
- Registra eventos de foco

### 3. Sistema de Pruebas (`test_llm_focus_system.py`)
- Prueba completa del sistema
- Verifica conexiones
- Prueba integración

## Configuración Requerida

### 1. Gemma2 LLM (Ollama)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar Gemma2
ollama pull gemma2

# Iniciar servidor
ollama serve
```

### 2. Zulip Server
- Servidor Zulip corriendo en `http://localhost`
- Bot configurado con API key
- Canal `desarrollo` creado

### 3. Configuración de Bots
Archivo `bot_config.json`:
```json
{
  "bots": [
    {
      "bot_name": "llm-analyzer",
      "email": "llm-analyzer-bot@localhost",
      "api_key": "YOUR_API_KEY_HERE"
    },
    {
      "bot_name": "focus-bot", 
      "email": "focus-bot@localhost",
      "api_key": "YOUR_API_KEY_HERE"
    }
  ]
}
```

## Instalación y Uso

### 1. Instalar Dependencias
```bash
pip install requests flask
```

### 2. Iniciar Sistema

**Terminal 1 - Webhook de Entrada:**
```bash
python incoming_focus_webhook.py
```

**Terminal 2 - Analyzer LLM:**
```bash
python llm_conversation_analyzer.py
```

### 3. Probar Sistema
```bash
python test_llm_focus_system.py
```

## Funcionalidades

### Análisis Inteligente
- Detección de cambios de tema con LLM
- Análisis contextual cada 20 segundos
- Identificación de temas técnicos vs no técnicos

### Recordatorios de Foco
- Mensajes contextuales con análisis LLM
- Sugerencias para mantener conversación enfocada
- Intervalo mínimo de 5 minutos entre recordatorios

### Registro y Estadísticas
- Log de eventos de foco en `focus_events.log`
- Endpoint `/stats` para estadísticas
- Health checks para monitoreo

## Endpoints del Webhook

- `POST /webhook` - Recibe recordatorios del LLM analyzer
- `POST /webhook/test` - Prueba de funcionalidad
- `GET /health` - Health check
- `GET /stats` - Estadísticas del sistema

## Ejemplo de Mensaje de Foco

```
@all Mantengamos el foco en la conversación técnica :light_bulb:

Contexto actual: desarrollo API REST
Tema anterior: React frontend
Nueva dirección: políticas empresa

Análisis LLM: cambio repentino a tema no técnico

Sugerencia: sugerir nuevo topic para tema no técnico

Para mejor organización:
- Si es un tema técnico relacionado, continuemos aquí
- Si es un tema diferente (no técnico), consideren abrir un nuevo topic
- Para temas variados, usen threads separados

Canal: #desarrollo | Timestamp: 12:48

---
Análisis automático con LLM - 2026-04-12 00:48:23
```

## Personalización

### Intervalo de Análisis
Modificar `analysis_interval` en `llm_conversation_analyzer.py`:
```python
self.analysis_interval = 20  # segundos
```

### Modelo LLM
Cambiar modelo en `llm_conversation_analyzer.py`:
```python
self.llm_model = "gemma2"  # o "llama2", "mistral", etc.
```

### Canal Objetivo
Modificar `target_stream` en ambos scripts:
```python
self.target_stream = "desarrollo"  # nombre del canal
```

## Troubleshooting

### LLM Connection Failed (404)
- Verificar que Ollama esté corriendo: `ollama serve`
- Chequear que Gemma2 esté instalado: `ollama list`
- Confirmar puerto 11434 esté disponible

### Zulip Connection Failed (400)
- Verificar servidor Zulip corriendo
- Chequear API key válida
- Confirmar configuración de bots

### Webhook Errors
- Verificar puertos 5000/5001 disponibles
- Chequear firewall
- Probar con `curl` manualmente

## Arquitectura

```
Zulip Channel (desarrollo)
    |
    v (cada 20s)
LLM Conversation Analyzer
    |
    v (webhook)
Incoming Focus Webhook
    |
    v (API)
Zulip (mensaje de foco)
```

## Mejoras Futuras

- [ ] Soporte para múltiples canales
- [ ] Configuración dinámica vía UI
- [ ] Integración con más modelos LLM
- [ ] Análisis de sentimiento
- [ ] Dashboard de métricas
- [ ] Notificaciones por Slack/Discord
