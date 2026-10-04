# 🎙️ Audiobook Generator

### 🚀 Audiobook Generator 1.0.0 (Python Edition)

Audiobook Generator es una aplicación de escritorio desarrollada en **Python (Tkinter)** orientada a la **generación de audiolibros a partir de documentos**, pensada como una herramienta modular para Windows.

El proyecto automatiza la lectura, procesamiento, división por capítulos, conversión mediante Text-to-Speech y generación final de archivos MP3.

**📦 Versión 1.0.0**

La versión 1.0.0 incorpora una aplicación Windows empaquetada en un ejecutable de un solo archivo y un instalador `.exe`, además de la ejecución tradicional desde Python. La distribución oficial se realiza mediante GitHub Releases.

---

<p align="center">
  <img src="images/screenshot.png?v=2" alt="Vista previa de Audiobook Generator" width="600"/>
</p>

---

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=flat&logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/language-Python-3776AB?style=flat&logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-Tkinter-FFDD54?style=flat)
![TTS](https://img.shields.io/badge/TTS-Edge%20TTS-blue?style=flat)
![Audio](https://img.shields.io/badge/output-MP3-5C2D91?style=flat)
![Status](https://img.shields.io/badge/status-stable-brightgreen?style=flat)
![OCR](https://img.shields.io/badge/OCR-Tesseract-success?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

---

## 🎯 Objetivo del proyecto

Audiobook Generator nace con el objetivo de ofrecer una herramienta modular para convertir documentos de texto en **audiolibros MP3**, automatizando el proceso de lectura, procesamiento, división por capítulos, conversión mediante Text-to-Speech y unión final del audio.

---

## ✨ Características principales

- 🎙️ Conversión de documentos a audiolibros MP3
- 📚 Procesamiento automático de capítulos
- ✂️ División automática de capítulos extensos en fragmentos
- 🔊 Text-to-Speech mediante `edge-tts`
- 🗣️ Perfiles de voz en español
- 🎛️ Control de velocidad, volumen y tono
- 📄 Soporte para TXT, Markdown, PDF, DOCX, EPUB, HTML, ODT y RTF
- 🧠 OCR para documentos PDF escaneados
- 🌐 Interfaz localizada
- 🖱️ Arrastrar y soltar documentos en Windows
- ⌨️ Navegación mediante `Tab`
- ↵ Atajo `Enter` para iniciar la generación
- 📊 Barra de progreso y estado del procesamiento
- 📂 Conservación opcional de capítulos MP3 individuales
- ⚙️ Configuración mediante archivos TOML
- 🧹 Limpieza automática del directorio temporal
- 🖥️ CLI y GUI utilizando el mismo núcleo de procesamiento
- 🧪 Suite automatizada de pruebas

### 🌍 Idiomas

Interfaz disponible en 9 idiomas:

**español, inglés, alemán, francés, italiano, portugués, ruso, japonés y chino**

La aplicación detecta automáticamente el idioma del sistema en Windows cuando existe una traducción disponible.

### 🎨 Interfaz y Windows

- Interfaz visual personalizada con tipografía Source Sans 3 y diseño oscuro
- Soporte mejorado para pantallas HiDPI/DPI scaling
- Iconografía nativa para ventana, barra de tareas y ejecutable de Windows
- Manejo de procesos externos sin abrir ventanas de consola en Windows
- Arrastrar y soltar validado en el ejecutable empaquetado

### 🎧 Audio

- Metadatos ID3 para pistas y audiolibro final
- Marcadores de capítulo navegables en el MP3 final cuando FFmpeg/ffprobe están disponibles
- Selección automática del directorio de salida cuando no se especifica uno
- Conservación opcional de capítulos MP3 individuales

---

## 🖼️ Interfaz

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

Además, la GUI incluye validación de archivos y parámetros, botón de información de la aplicación, estados de procesamiento y comportamiento adaptado a Windows.

El campo Documento acepta arrastrar y soltar archivos compatibles. Las teclas `Backspace`/`Delete` permiten limpiar los campos de ruta y `Enter` inicia la generación desde la ventana principal.

Si no se selecciona manualmente un directorio de salida, la aplicación utiliza automáticamente el directorio del documento de entrada.

La interfaz detecta automáticamente el idioma del sistema cuando existe una traducción disponible. También puede forzarse un idioma mediante la variable de entorno `AUDIOBOOK_GENERATOR_LANGUAGE`.

Idiomas disponibles:

`de` · `en` · `es` · `fr` · `it` · `ja` · `pt` · `ru` · `zh`

Durante la generación se utiliza el directorio temporal:

```text
.audiobook_generator_temp/
```

Este directorio se elimina automáticamente al finalizar el trabajo de la GUI.

---

## 📷 Capturas de pantalla

<p align="center">
  <img src="images/screenshot.png?v=2" alt="Vista previa de Audiobook Generator" width="600"/>
</p>

---

## 📄 Formatos de entrada

Audiobook Generator incluye lectores para:

- TXT
- Markdown (`.md`, `.markdown`)
- PDF
- DOCX
- EPUB
- HTML
- ODT
- RTF

---

## 🧠 OCR para PDF

Audiobook Generator incorpora procesamiento OCR para documentos PDF que contienen páginas escaneadas.

Se pueden utilizar tres modos:

```text
auto
always
never
```

Ejemplo:

```powershell
python -m audiobook_generator.cli --ocr auto
```

También pueden configurarse:

```powershell
--ocr-language "spa"
--ocr-dpi 300
--ocr-psm 6
```

Para documentos en español e inglés:

```powershell
--ocr-language "spa+eng"
```

Para diagnóstico:

```powershell
--debug-ocr
```

El OCR utiliza PyMuPDF, Tesseract y Pillow.

En la versión 1.0.0 el procesamiento OCR incorpora validaciones de confianza y limpieza de ruido para reducir la incorporación de texto procedente de sellos, firmas, fondos y elementos gráficos. Cuando la primera segmentación no produce suficiente texto útil, se utiliza una pasada alternativa de Tesseract para intentar recuperar el contenido.

---

## 🔊 Voces

La aplicación incluye perfiles de voz en español, entre ellos:

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

### Velocidad

```powershell
--rate "+10%"
```

### Volumen

```powershell
--volume "+10%"
```

### Tono

```powershell
--pitch "+2Hz"
```

### Fragmentación

```powershell
--max-characters 1500
```

El valor debe ser mayor que cero.

---

## 📚 Capítulos

El sistema identifica automáticamente estructuras de capítulos.

Cuando un capítulo supera el límite máximo de caracteres, se divide automáticamente en fragmentos adecuados para el procesamiento TTS.

Los capítulos individuales pueden conservarse mediante:

```powershell
--keep-chapters
```

El audiolibro final incorpora metadatos de título/álbum y, cuando es posible obtener las duraciones de cada pista mediante `ffprobe`, también incluye marcadores de capítulo navegables con los títulos detectados.

---

## 📥 Descarga e instalación

### ⭐ Recomendado para usuarios de Windows

Para la versión 1.0.0 no es necesario instalar Python ni ejecutar comandos desde una terminal. Se recomienda utilizar el instalador oficial publicado en GitHub Releases.

### 1. Descargar el instalador

**[⬇️ Descargar Audiobook Generator 1.0.0 — Instalador para Windows](https://github.com/Pablitus666/Audiobook-Generator/releases/download/v1.0.0/AudiobookGenerator-Setup-1.0.0.zip)**

También puedes consultar todos los archivos de la versión:

**[📦 Ver GitHub Releases](https://github.com/Pablitus666/Audiobook-Generator/releases)**

### 2. Instalar la aplicación

1. Descarga `AudiobookGenerator-Setup-1.0.0.zip`.
2. Extrae el contenido del archivo ZIP en una carpeta.
3. Ejecuta el instalador `.exe` incluido.
4. Sigue las instrucciones del instalador.
5. Una vez finalizada la instalación, abre **Audiobook Generator** desde el acceso directo creado.

> **Nota:** el archivo publicado en GitHub Releases es un ZIP que contiene el instalador de Windows.

### 🔐 Verificación SHA-256

SHA-256 del archivo `AudiobookGenerator-Setup-1.0.0.zip`:

```text
b5af38904f6144374c527613b694d4204737b3b444ffe6ff75565ff0ff1143b4
```

Puedes comprobar la integridad del archivo descargado desde PowerShell:

```powershell
Get-FileHash .\AudiobookGenerator-Setup-1.0.0.zip -Algorithm SHA256
```

El valor obtenido debe coincidir con el SHA-256 indicado arriba.

### 🪟 Aplicación portátil

También existe un ejecutable portátil de un solo archivo (`AudiobookGenerator.exe`) para utilizar la aplicación sin realizar una instalación tradicional.

La versión empaquetada mantiene la funcionalidad principal de la GUI:

- Arrastrar y soltar
- Selección de voz
- Control de velocidad, volumen y tono
- OCR
- Procesamiento por capítulos
- Barra de progreso
- Generación del MP3 final

**Edge TTS requiere conexión a Internet.**

---

## 🚀 Uso normal

### Opción 1: Interfaz gráfica

Desde el entorno virtual:

```powershell
python -m audiobook_generator.gui
```

También está disponible:

```powershell
audiobook-generator-gui
```

### Opción 2: Ejecución mediante CLI

Ejemplo:

```powershell
python -m audiobook_generator.cli `
    --input "libro.txt" `
    --output ".\output"
```

Si se omite `--output`, se utiliza automáticamente el directorio donde se encuentra el documento de entrada.

Para consultar todas las opciones:

```powershell
python -m audiobook_generator.cli --help
```

---

## 🧱 Arquitectura del proyecto

```text
Audiobook-Generator/
│
├── audiobook_generator/
│   ├── audio/          # Procesamiento y generación de audio
│   ├── core/           # Pipeline y lógica principal
│   ├── gui/            # Interfaz gráfica
│   ├── ocr/            # Procesamiento OCR
│   ├── readers/        # Lectores de documentos
│   └── tts/            # Integración con Text-to-Speech
│
├── assets/             # Recursos gráficos y traducciones
├── docs/               # Documentación
├── examples/           # Ejemplos
├── images/             # Imágenes del proyecto
│
├── tools/
│   ├── ffmpeg/         # Herramientas FFmpeg para Windows
│   └── tesseract/      # Componentes Tesseract para OCR en Windows
│
├── tests/              # Pruebas automatizadas
│
├── .gitignore
├── pyproject.toml
├── README.md
├── RELEASE_DESCRIPTION.md
└── requirements.txt
```

---

## 🛠️ Instalación para desarrollo

Para trabajar con el código fuente:

### 1. Crear el entorno virtual

```powershell
python -m venv .venv
```

### 2. Activarlo

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar el proyecto

```powershell
python -m pip install -e ".[dev,gui,docs,ocr]"
```

### Requisitos para ejecutar desde el código fuente

- Python `3.10` o superior
- FFmpeg disponible en `PATH`
- Tesseract instalado para utilizar OCR
- Conexión a Internet para Edge TTS

> Estos requisitos corresponden a la ejecución desde el código fuente. La distribución Windows de la versión 1.0.0 se entrega como aplicación empaquetada mediante GitHub Releases.

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
bitrate = "192k"

[processing]
max_characters = 1500
temp_dir = "temp"
keep_chapters = true
```

Las opciones proporcionadas directamente mediante CLI tienen prioridad sobre los valores definidos en el archivo TOML.

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

## 📦 Distribución y release

La versión 1.0.0 se construye con **PyInstaller** como ejecutable Windows de un solo archivo y se empaqueta con **Inno Setup** para generar el instalador.

Los artefactos de distribución no forman parte del repositorio fuente y se publican como archivos adjuntos de GitHub Releases.

El repositorio conserva el código fuente, recursos, configuración de build y documentación; los ejecutables, instaladores y materiales privados de firma se mantienen fuera del control de versiones.

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
- ✔️ Ejecutable `.exe` de un solo archivo
- ✔️ Instalador Windows `.exe` para la versión 1.0.0
- ✔️ Arrastrar y soltar validado en el ejecutable empaquetado
- ✔️ Ejecución portátil validada
- ✔️ Generación de audiolibros largos validada en la aplicación empaquetada
- ✔️ Salida automática junto al documento cuando no se selecciona directorio
- ✔️ Metadatos de audio y marcadores de capítulo
- ✔️ Interfaz multilingüe con detección automática del idioma del sistema
- ✔️ Soporte HiDPI y recursos gráficos integrados

---

## 🔮 Posibles mejoras futuras

- Reproducción y previsualización del audio
- Gestión visual avanzada de capítulos
- Mejoras de diagnóstico y registro
- Incorporación de nuevos motores TTS
- Distribución y automatización de releases para futuras versiones
- Nuevas mejoras del instalador `.exe`

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

---

## 🤝 Contribuciones

Las contribuciones, sugerencias y mejoras son bienvenidas.

Si encuentras un problema o tienes una idea, no dudes en abrir un *issue* o *pull request*.

---

## 👨‍💻 Autor

**Walter Pablo Téllez Ayala**  
Software Developer  
📍 Bolivia 🇧🇴  
📧 pharmakoz@gmail.com

© 2026 — Audiobook Generator
