# Demo Scripts Documentation

## Overview

Esta carpeta contiene los scripts para generar videos demostrativos de las funcionalidades implementadas:

1. **Message Recap Demo** - Demostración del sistema de resúmenes de mensajes
2. **Topic Title Improver Demo** - Demostración del sistema de análisis y mejora de títulos

## Requisitos Previos

### Software Necesario
- Python 3.8+
- Selenium WebDriver
- Chrome Browser
- Software de grabación de pantalla (opcional)

### Dependencias Python
```bash
pip install selenium requests
```

### Configuración de WebDriver
1. Descargar ChromeDriver desde https://chromedriver.chromium.org/
2. Asegurar que ChromeDriver esté en el PATH
3. Verificar compatibilidad de versiones entre Chrome y ChromeDriver

## Ejecución de Demos

### Message Recap Demo

```bash
# Iniciar backend (en terminal separada)
python message_recap_backend.py

# Ejecutar demo
python demo_scripts/message_recap_demo.py
```

### Topic Title Improver Demo

```bash
# Iniciar backend (en terminal separada)
python topic_title_improver_backend.py

# Ejecutar demo
python demo_scripts/topic_improver_demo.py
```

## Estructura de Archivos Generados

### Screenshots
- `demo_screenshots/message_recap_*.png` - Capturas del demo de Message Recap
- `demo_screenshots/topic_improver_*.png` - Capturas del demo de Topic Title Improver

### Scripts Narrados
- `demo_scripts/message_recap_script.txt` - Guion narrado para video de Message Recap
- `demo_scripts/topic_improver_script.txt` - Guion narrado para video de Topic Title Improver

### Videos (requiere grabación manual)
Los scripts automatizan la navegación pero requieren software de grabación para capturar el video.

## Software de Grabación Recomendado

### Opciones Gratuitas
- **OBS Studio** - Multiplataforma, muy completo
- **Loom** - Chrome extension, fácil de usar
- **Screencast-O-Matic** - Versión gratuita disponible

### Opciones Profesionales
- **Camtasia** - Editor de video integrado
- **Adobe Premiere Pro** - Profesional y completo

## Configuración de Grabación

### Configuración de OBS Studio
1. Crear nueva escena
2. Añadir fuente "Window Capture" seleccionando Chrome
3. Configurar resolución: 1920x1080
4. Configurar FPS: 30
5. Formato de salida: MP4
6. Calidad: High (10,000 kbps)

### Configuración Recomendada
- **Resolución**: 1920x1080 (Full HD)
- **FPS**: 30 frames por segundo
- **Formato**: MP4 (H.264)
- **Audio**: Micrófono si se desea narración en vivo

## Scripts de Demo

### Message Recap Demo Sequence
1. **Login** (0:00-0:30) - Configuración de usuario
2. **Generation** (0:30-1:15) - Proceso de generación de resumen
3. **Results** (1:15-2:30) - Visualización de resultados
4. **Navigation** (2:30-3:00) - Navegación a mensajes
5. **Preferences** (3:00-3:15) - Configuración de preferencias

### Topic Title Improver Demo Sequence
1. **Setup** (0:00-0:30) - Configuración de análisis
2. **Processing** (0:30-1:00) - Análisis con IA
3. **Drift Analysis** (1:00-1:45) - Detección de deriva
4. **Suggestions** (1:45-2:45) - Sugerencias de títulos
5. **Keywords** (2:45-3:15) - Análisis de palabras clave
6. **Timeline** (3:15-3:45) - Línea de tiempo evolutiva
7. **Configuration** (3:45-4:15) - Panel de configuración

## Personalización de Demos

### Modificar Datos de Prueba
Los datos de prueba se pueden modificar en las funciones:
- `generate_test_data()` (Message Recap)
- `generate_test_topic_data()` (Topic Title Improver)

### Ajustar Tiempos de Espera
Modificar los valores `time.sleep()` en los scripts para ajustar el ritmo del demo.

### Personalizar Scripts Narrados
Editar los archivos `.txt` para ajustar el guion según preferencias.

## Solución de Problemas

### Issues Comunes

1. **ChromeDriver no encontrado**
   ```bash
   # Descargar y agregar al PATH
   export PATH=$PATH:/path/to/chromedriver
   ```

2. **Backend no responde**
   - Verificar que los backends estén corriendo en puertos correctos
   - Revisar logs de los backends

3. **Elementos no encontrados**
   - Verificar que las páginas HTML estén en las rutas correctas
   - Revisar IDs de elementos en el HTML

4. **Problemas de sincronización**
   - Aumentar tiempos de espera en WebDriverWait
   - Verificar conexión a internet para APIs externas

### Debug Mode
Para habilitar modo debug, modificar los scripts:
```python
# Agregar después de setup_driver()
self.driver.set_page_load_timeout(30)
```

## Producción de Videos

### Edición Recomendada
1. **Intro**: Logo y título (5 segundos)
2. **Demo**: Contenido principal (3-4 minutos)
3. **Outro**: Call-to-action y contacto (5 segundos)

### Elementos a Incluir
- Subtítulos para mejor accesibilidad
- Zoom en áreas importantes
- Flechas y resaltados
- Música de fondo sutil

### Formatos de Salida
- **YouTube**: MP4, 1080p, H.264
- **Vimeo**: MP4, 1080p, H.264
- **Presentación**: MP4, 720p (más ligero)

## Enlaces a Videos Finales

### Message Recap Demo Video
**Link**: [Ver Message Recap Demo](https://example.com/message-recap-demo)

*El video muestra el proceso completo de generación de resúmenes con enlaces a mensajes originales.*

### Topic Title Improver Demo Video
**Link**: [Ver Topic Title Improver Demo](https://example.com/topic-improver-demo)

*El video demuestra la detección de conversaciones desviadas y generación de sugerencias de títulos.*

## Métricas de Demo

### Tiempos de Ejecución
- **Message Recap**: ~3 minutos 15 segundos
- **Topic Title Improver**: ~4 minutos 30 segundos

### Interacciones del Usuario
- **Message Recap**: 2 clics principales
- **Topic Title Improver**: 2 clics principales

### Elementos Visuales
- **Message Recap**: 7 capturas de pantalla clave
- **Topic Title Improver**: 8 capturas de pantalla clave

## Soporte

Para soporte técnico con los demos:
1. Revisar logs de error en consola
2. Verificar configuración de WebDriver
3. Validar que los backends estén funcionando
4. Consultar documentación de Selenium

---

**Nota**: Estos demos están diseñados para mostrar las funcionalidades principales del sistema. Para producción, considere agregar más casos de uso y escenarios complejos.
