# 🎙️ Audiobook Generator

### 🚀 Audiobook Generator 1.0.0 (Python Edition)

Audiobook Generator es una aplicación de escritorio desarrollada en **Python (Tkinter)** orientada a la **generación de audiolibros a partir de documentos**, pensada como una herramienta modular para Windows.

El proyecto automatiza la lectura, procesamiento, división por capítulos, conversión mediante Text-to-Speech y generación final de archivos MP3.

---

![Social Preview](images/Preview.png)

---

#### ✨ Novedades principales

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

Audiobook Generator está diseñado para ofrecer una experiencia clara y modular, separando la interfaz gráfica, la CLI y el núcleo de procesamiento.

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=flat&logo=windows&logoColor=white) ![Language](https://img.shields.io/badge/language-Python-3776AB?style=flat&logo=python&logoColor=white) ![UI](https://img.shields.io/badge/UI-Tkinter-FFDD54?style=flat) ![TTS](https://img.shields.io/badge/TTS-Edge%20TTS-blue?style=flat) ![Audio](https://img.shields.io/badge/output-MP3-5C2D91?style=flat) ![Status](https://img.shields.io/badge/status-stable-brightgreen?style=flat) ![OCR](https://img.shields.io/badge/OCR-Tesseract-success?style=flat) ![License](https://img.shields.io/badge/license-MIT-green?style=flat)

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
- 📄 Soporte para TXT, PDF, DOCX, EPUB, HTML, ODT y RTF
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
├── assets/              # Recursos gráficos y traducciones
├── docs/                # Documentación
├── examples/            # Ejemplos
├── images/              # Imágenes del proyecto
├── tests/               # Pruebas automatizadas
│
├── .gitignore
├── pyproject.toml
├── README.md
├── RELEASE_DESCRIPTION.md
└── requirements.txt
```

---

#### 📥 Descarga e instalación

👉 Descargar la versión disponible desde GitHub Releases:

https://github.com/Pablitus666/Audiobook-Generator/releases

Para utilizar Audiobook Generator desde el código fuente:

- Instalar Python 3.10 o superior
- Crear un entorno virtual
- Instalar las dependencias del proyecto
- Tener FFmpeg disponible en `PATH`
- Disponer de conexión a Internet para utilizar Edge TTS

---

## 🚀 Ejecución Uso normal

### Opción 1: Interfaz gráfica

Desde el entorno virtual:

```powershell
python -m audiobook_generator.gui
```

También está disponible:

```powershell
audiobook-generator-gui
```

---

### Opción 2: Ejecución mediante CLI

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

## 🔮 Posibles mejoras futuras

- Reproducción y previsualización del audio
- Gestión visual avanzada de capítulos
- Mejoras de diagnóstico y registro
- Incorporación de nuevos motores TTS
- Empaquetado independiente para Windows
- Instalador `.exe`

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

📍 Bolivia 🇧🇴 <img src="https://flagcdn.com/w20/bo.png" width="20"/><br>

📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com)

© 2026 — Audiobook Generator
