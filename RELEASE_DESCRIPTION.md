# 🚀 Audiobook Generator — Notas de Versión

## Versión 1.0.0 — Lanzamiento inicial consolidado

Audiobook Generator `1.0.0` reúne el núcleo de conversión de documentos a audiolibros MP3, la interfaz de línea de comandos (CLI), OCR para PDF y una interfaz gráfica de escritorio para Windows.

La versión mantiene una arquitectura modular en la que la GUI utiliza el mismo pipeline de lectura, procesamiento, Text-to-Speech y FFmpeg, sin duplicar la lógica de negocio.

---

## ✨ Características principales

### 📚 Conversión de documentos

Se incluyen lectores para:

- TXT
- PDF
- DOCX
- EPUB
- HTML
- ODT
- RTF

El formato se detecta automáticamente y el contenido se transforma al modelo interno utilizado por el pipeline.

### 🖥️ Interfaz gráfica

La versión incluye una GUI basada en Tkinter, orientada al uso en Windows. Permite:

- seleccionar el documento de entrada mediante explorador de archivos;
- arrastrar y soltar documentos compatibles sobre el campo de entrada;
- seleccionar el directorio de salida;
- seleccionar voz, velocidad, volumen, tono y tamaño máximo de fragmento;
- conservar o no los capítulos MP3 individuales;
- iniciar la generación desde un botón gráfico;
- utilizar `Tab` para la navegación por teclado;
- utilizar `Enter` como atajo para iniciar la generación;
- limpiar las rutas seleccionadas con `Backspace` o `Delete`;
- visualizar el porcentaje y el estado del procesamiento;
- recibir diálogos visuales para advertencias, errores y finalización correcta.

Después de una generación completada correctamente, la GUI reinicia el progreso y limpia los campos de entrada y salida para preparar el siguiente trabajo. El audiolibro generado y la carpeta `chapters/`, cuando se solicita conservar capítulos, permanecen en el directorio de salida.

El directorio temporal `.audiobook_generator_temp` se elimina automáticamente al finalizar el trabajo de la GUI, incluso cuando se produce un error durante la generación.

La GUI puede ejecutarse mediante:

```powershell
python -m audiobook_generator.gui
```

o mediante el comando instalado:

```powershell
audiobook-generator-gui
```

### 🌍 Localización

La interfaz detecta automáticamente el idioma del sistema y dispone de traducciones para:

- alemán (`de`)
- inglés (`en`)
- español (`es`)
- francés (`fr`)
- italiano (`it`)
- japonés (`ja`)
- portugués (`pt`)
- ruso (`ru`)
- chino (`zh`)

El inglés se utiliza como idioma de respaldo cuando el idioma detectado no está soportado.

### 🧩 Pipeline modular

El procesamiento se organiza en etapas independientes:

```text
Documento
   ↓
ReaderFactory
   ↓
Preprocesamiento
   ↓
Capítulos
   ↓
Fragmentación
   ↓
Edge TTS
   ↓
MP3
   ↓
FFmpeg
   ↓
Audiolibro final
```

Esta separación permite que la GUI y la CLI utilicen el mismo núcleo de procesamiento.

### 🔊 Voces

Se incluyen cuatro perfiles de voz:

| Nombre | Idioma | Voz técnica |
|---|---|---|
| `Sofía` | Español (Bolivia) | `es-BO-SofiaNeural` |
| `Elvira` | Español (España) | `es-ES-ElviraNeural` |
| `Marcelo` | Español (Bolivia) | `es-BO-MarceloNeural` |
| `Álvaro` | Español (España) | `es-ES-AlvaroNeural` |

La CLI permite consultar el catálogo mediante:

```powershell
python -m audiobook_generator.cli --list-voices
```

También acepta directamente identificadores de voz compatibles con Edge TTS y conserva alias de compatibilidad para configuraciones anteriores.

### 🎛️ Control TTS

La aplicación permite configurar:

- voz;
- velocidad;
- volumen;
- tono;
- tamaño máximo de fragmento;
- bitrate MP3.

### 📖 Capítulos

El sistema detecta estructuras de capítulos y divide capítulos extensos en fragmentos adecuados para TTS.

Los capítulos MP3 individuales pueden conservarse mediante `--keep-chapters` en la CLI o mediante el interruptor correspondiente en la GUI.

### 🧠 OCR

El procesamiento OCR de PDF admite:

```text
auto
always
never
```

También permite configurar idioma, DPI, modo de segmentación de Tesseract y diagnóstico OCR.

La documentación específica se encuentra en:

```text
docs/OCR.md
```

---

## ⚙️ Configuración

Audiobook Generator admite archivos TOML para centralizar parámetros de TTS, salida y procesamiento. Las opciones proporcionadas explícitamente mediante CLI tienen prioridad sobre la configuración del archivo TOML.

---

## 🧪 Validación y pruebas

La validación actual del proyecto mediante la suite automatizada es:

```text
226 passed, 1 skipped
```

El test omitido corresponde a:

```text
tests/test_integration_real.py
```

Está desactivado por defecto porque utiliza servicios y herramientas reales. Puede ejecutarse explícitamente con:

```powershell
$env:RUN_REAL_INTEGRATION="1"
python -m pytest tests\test_integration_real.py -v
```

Además de la suite automatizada, la GUI fue ejecutada desde el entorno virtual y se verificó una generación real de cuatro etapas, con salida registrada hasta:

```text
[1/4] Generando: Resumen Completo
[2/4] Generando: Resumen Completo
[3/4] Generando: Resumen Completo
[4/4] Generando: Resumen Completo
```

La generación TTS requiere conectividad a Edge TTS y la generación final del audiolibro requiere FFmpeg disponible en `PATH`.

---

## 💻 Entorno de desarrollo

El paquete declara:

```text
Python >= 3.10
```

La aplicación se ha validado en Windows con Python de la serie 3.14 y un entorno virtual `.venv`.

Para la GUI se utilizan Tkinter, Pillow y `tkinterdnd2` como dependencia opcional de arrastrar y soltar. Las funciones OCR requieren además Tesseract instalado localmente.

---

## 📦 Distribución

La versión `1.0.0` se distribuye como proyecto Python y CLI, e incluye la interfaz gráfica.

El repositorio utiliza el tag:

```text
v1.0.0
```

Repositorio:

https://github.com/Pablitus666/Audiobook-Generator

Esta versión **no incluye todavía un instalador `.exe` independiente**. El empaquetado para Windows queda planificado para una etapa posterior.

---

## 🗺️ Próximas etapas

Entre las líneas de evolución previstas se encuentran:

- reproducción y previsualización del audio;
- gestión visual más avanzada de capítulos;
- mejoras de diagnóstico y registro;
- nuevos motores TTS cuando resulte conveniente;
- empaquetado y distribución independiente para Windows;
- un posible instalador `.exe`.

---

## 👨‍💻 Créditos

**Walter Pablo Téllez Ayala**  
Software Developer  
📍 Bolivia 🇧🇴
📧 pharmakoz@gmail.com

**Versión:** 1.0.0  
**Proyecto:** Audiobook Generator  
© 2026 — Audiobook Generator

---

## 📄 Licencia

Audiobook Generator se distribuye bajo la licencia **MIT**.
