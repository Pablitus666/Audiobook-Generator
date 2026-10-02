# 🎙️ Audiobook Generator

### 🚀 Audiobook Generator 1.0.0 (Python Edition)

Primera versión de **Audiobook Generator**, una aplicación de escritorio desarrollada en **Python (Tkinter)** orientada a la generación de audiolibros a partir de documentos.

El proyecto automatiza la lectura, procesamiento, división por capítulos, conversión mediante Text-to-Speech y generación final de archivos MP3.

---

## 🎯 Objetivo de esta versión

Esta versión establece la base funcional de Audiobook Generator como una herramienta modular para Windows, separando claramente:

- La interfaz gráfica (GUI)
- La interfaz de línea de comandos (CLI)
- El procesamiento de documentos
- El procesamiento OCR
- La generación de audio mediante Text-to-Speech
- El procesamiento y división por capítulos

---

## ✨ Novedades principales

- 🎙️ Conversión de documentos a audiolibros MP3
- 🖥️ Interfaz gráfica para Windows mediante Tkinter
- ⌨️ Navegación mediante teclado
- 🖱️ Arrastrar y soltar documentos
- 🔊 Text-to-Speech mediante Edge TTS
- 📚 Procesamiento automático por capítulos
- ✂️ Fragmentación automática de capítulos extensos
- 🧠 OCR para documentos PDF escaneados
- 🌐 Interfaz localizada
- ⚙️ Configuración mediante archivos TOML
- 🧪 Suite automatizada de pruebas
- 🧹 Limpieza automática de archivos temporales
- 🎧 Conservación opcional de capítulos MP3 individuales

---

## 🖼️ Interfaz gráfica

La aplicación incorpora una interfaz gráfica desarrollada con **Tkinter**, orientada al uso en Windows.

La ventana principal permite:

- Seleccionar documentos mediante el explorador de archivos
- Arrastrar y soltar documentos compatibles
- Seleccionar el directorio de salida
- Seleccionar la voz
- Configurar velocidad, volumen y tono
- Configurar el tamaño máximo de fragmento
- Activar o desactivar la conservación de capítulos
- Iniciar la generación del audiolibro
- Visualizar el progreso del procesamiento
- Navegar mediante teclado

Durante la generación se utiliza el directorio temporal:

```text
.audiobook_generator_temp/
```

Este directorio se elimina automáticamente al finalizar el trabajo de la GUI.

---

## 📄 Formatos de entrada

Audiobook Generator incluye lectores para:

- TXT
- PDF
- DOCX
- EPUB
- HTML
- ODT
- RTF

---

## 🧠 OCR para PDF

Esta versión incorpora procesamiento OCR para documentos PDF que contienen páginas escaneadas.

Se pueden utilizar tres modos:

```text
auto
always
never
```

También permite configurar:

```text
--ocr-language "spa"
--ocr-dpi 300
--ocr-psm 6
```

Para documentos en español e inglés:

```text
--ocr-language "spa+eng"
```

Para diagnóstico:

```text
--debug-ocr
```

El OCR utiliza PyMuPDF, Tesseract y Pillow.

---

## 🔊 Voces

La aplicación incluye perfiles de voz en español:

| Perfil | Idioma | Voz técnica |
|---|---|---|
| `Sofía` | Español (Bolivia) | `es-BO-SofiaNeural` |
| `Elvira` | Español (España) | `es-ES-ElviraNeural` |
| `Marcelo` | Español (Bolivia) | `es-BO-MarceloNeural` |
| `Álvaro` | Español (España) | `es-ES-AlvaroNeural` |

También es posible consultar el catálogo disponible mediante:

```powershell
python -m audiobook_generator.cli --list-voices
```

---

## 🎛️ Control del audio

La generación permite configurar:

### Velocidad

```text
--rate "+10%"
```

### Volumen

```text
--volume "+10%"
```

### Tono

```text
--pitch "+2Hz"
```

### Fragmentación

```text
--max-characters 1500
```

El valor máximo de caracteres debe ser mayor que cero.

---

## 📚 Capítulos

El sistema identifica automáticamente estructuras de capítulos.

Cuando un capítulo supera el límite máximo de caracteres, se divide automáticamente en fragmentos adecuados para el procesamiento TTS.

Los capítulos individuales pueden conservarse mediante:

```text
--keep-chapters
```

---

## ⚙️ Configuración TOML

Audiobook Generator permite definir parámetros mediante archivos TOML.

Ejemplo:

```toml
[tts]
voice = "es-ES-ElviraNeural"
rate = "+0%"
volume = "+0%"
pitch = "+0Hz"

[output]
format = "mp3"
bitrate = "160k"

[processing]
max_characters = 1500
temp_dir = "temp"
keep_chapters = true
```

Las opciones proporcionadas directamente mediante CLI tienen prioridad sobre los valores definidos en el archivo TOML.

---

## 🚀 Ejecución

### Interfaz gráfica

```powershell
python -m audiobook_generator.gui
```

También está disponible:

```powershell
audiobook-generator-gui
```

### CLI

Ejemplo:

```powershell
python -m audiobook_generator.cli `
    --input "libro.txt" `
    --output ".\output"
```

Para consultar todas las opciones:

```powershell
python -m audiobook_generator.cli --help
```

---

## 🛠️ Instalación para desarrollo

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar el proyecto:

```powershell
python -m pip install -e ".[dev,gui,docs,ocr]"
```

---

## 🧪 Testing

La suite automatizada se ejecuta mediante:

```powershell
python -m pytest -q
```

Estado de las pruebas:

```text
226 passed, 1 skipped
```

El test omitido corresponde a la integración real, desactivada por defecto.

Para ejecutarla:

```powershell
$env:RUN_REAL_INTEGRATION="1"

python -m pytest tests\test_integration_real.py -v
```

---

## 📦 Requisitos

- Python `3.10` o superior
- FFmpeg disponible en `PATH`
- Conexión a Internet para Edge TTS
- Tesseract instalado para utilizar OCR

---

## 📦 Estado del proyecto

- ✔️ Versión `1.0.0`
- ✔️ CLI funcional
- ✔️ Interfaz gráfica funcional
- ✔️ Soporte para múltiples formatos de entrada
- ✔️ OCR integrado
- ✔️ Procesamiento por capítulos
- ✔️ Text-to-Speech mediante Edge TTS
- ✔️ Configuración TOML
- ✔️ Suite automatizada de pruebas
- ✔️ Compatible con Windows

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

---

## 👨‍💻 Autor

**Walter Pablo Téllez Ayala**

Software Developer

📍 Bolivia 🇧🇴

📧 pharmakoz@gmail.com

© 2026 — Audiobook Generator
