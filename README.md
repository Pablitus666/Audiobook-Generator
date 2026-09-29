# Audiobook Generator

Aplicación modular para convertir documentos de texto en audiolibros MP3 mediante Text-to-Speech (TTS).

**Versión:** `1.0.0`

## Características

* Conversión de documentos a audiolibros MP3.
* Arquitectura modular y desacoplada.
* Procesamiento por capítulos y fragmentos.
* Motor TTS basado en `edge-tts`.
* Cuatro perfiles de voz incluidos:

  * `Sofía` — Sofía
  * `Elvira` — Elvira
  * `Marcelo` — Marcelo
  * `Álvaro` — Álvaro
* Configuración de velocidad, volumen y tono.
* División automática de contenido en capítulos.
* División de capítulos extensos en fragmentos para TTS.
* Unión de capítulos mediante FFmpeg.
* Conservación opcional de los capítulos MP3 individuales.
* Configuración mediante archivo TOML.
* Soporte OCR para documentos PDF escaneados.
* Modo de diagnóstico OCR.
* CLI disponible mediante `python -m audiobook_generator` y `audiobook-generator`.
* Suite automatizada de pruebas.

## Formatos de entrada

La versión `1.0.0` incluye lectores para:

* TXT
* PDF
* DOCX
* EPUB
* HTML
* ODT
* RTF

El sistema selecciona automáticamente el lector correspondiente según el formato del archivo de entrada.

## Arquitectura

El flujo principal del sistema es:

```text
                    Documento
                        │
                        ▼
                  ReaderFactory
                        │
                        ▼
                  Documento interno
                        │
                        ▼
                Preprocesamiento
                        │
                        ▼
                División en capítulos
                        │
                        ▼
                 Fragmentación TTS
                        │
                        ▼
                    Edge TTS
                        │
                        ▼
              MP3 por capítulo/fragmento
                        │
                        ▼
                     FFmpeg
                        │
                        ▼
               Audiolibro MP3 final
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       capítulos MP3         archivo final
       opcionales             Audiobook.mp3
```

Las responsabilidades están separadas:

* **Readers:** convierten los diferentes formatos de entrada a modelos internos.
* **Preprocessor:** limpia y prepara el texto.
* **Splitter:** identifica capítulos y divide contenido extenso.
* **TTS:** convierte los fragmentos de texto en audio.
* **FFmpeg:** une los archivos MP3.
* **Pipeline:** coordina todo el proceso.
* **CLI:** proporciona la interfaz de línea de comandos.

La futura interfaz gráfica deberá utilizar este pipeline sin incorporar lógica de negocio directamente en la GUI.

## Requisitos

### Software

* Python `3.10` o superior.
* FFmpeg disponible en `PATH`.
* Conexión a Internet para utilizar Edge TTS.

### TTS

El motor actual utiliza `edge-tts`, que actúa como cliente para el servicio de Text-to-Speech de Microsoft Edge.

Por lo tanto, la generación de audio requiere conectividad de red.

### GPU

La generación TTS actual **no requiere GPU**.

El procesamiento de texto, la división de capítulos y la comunicación con Edge TTS no utilizan una GPU local como requisito del proyecto.

El sistema está diseñado para funcionar mediante CPU y servicios externos, por lo que una GPU dedicada no es necesaria para la arquitectura actual.

## Instalación

Se recomienda utilizar un entorno virtual.

### Crear entorno virtual

```powershell
python -m venv .venv
```

### Activarlo en PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar el proyecto

Para instalar el paquete junto con todas las dependencias necesarias para desarrollo, documentación y OCR:

```powershell
python -m pip install -e ".[dev,docs,ocr]"
```

La instalación completa incluye:

* `pytest`
* `pytest-asyncio`
* `reportlab`
* `pypdf`
* `python-docx`
* `pymupdf`
* `pytesseract`
* `Pillow`

## Dependencias opcionales

### Documentos

Las dependencias relacionadas con PDF y DOCX pueden instalarse mediante:

```powershell
python -m pip install -r requirements-docs.txt
```

O mediante el extra equivalente del paquete:

```powershell
python -m pip install -e ".[docs]"
```

### OCR

Para habilitar el procesamiento OCR de PDF:

```powershell
python -m pip install -r requirements-ocr.txt
```

O mediante el extra equivalente:

```powershell
python -m pip install -e ".[ocr]"
```

El OCR utiliza:

* PyMuPDF
* Tesseract
* Pillow

Además de las dependencias Python, Tesseract debe estar instalado y disponible para el sistema cuando se utilice OCR.

## Uso básico

La forma general de ejecutar el programa es:

```powershell
python -m audiobook_generator.cli `
    --input "libro.txt" `
    --output ".\output"
```

También puede utilizarse el comando instalado:

```powershell
audiobook-generator `
    --input "libro.txt" `
    --output ".\output"
```

Para consultar todas las opciones:

```powershell
python -m audiobook_generator.cli --help
```

## Conversión de un PDF

Por ejemplo:

```powershell
python -m audiobook_generator.cli `
    --input "libro.pdf" `
    --output ".\output\libro"
```

Para PDFs que pueden contener páginas escaneadas:

```powershell
python -m audiobook_generator.cli `
    --input "libro.pdf" `
    --output ".\output\libro" `
    --ocr auto
```

## OCR

El procesamiento OCR admite tres modos:

```text
auto
always
never
```

### `auto`

Detecta automáticamente las páginas que necesitan OCR.

```powershell
--ocr auto
```

### `always`

Fuerza el procesamiento OCR:

```powershell
--ocr always
```

### `never`

Desactiva OCR:

```powershell
--ocr never
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

### Diagnóstico OCR

Para conservar información adicional durante el procesamiento:

```powershell
--debug-ocr
```

Para desactivar explícitamente esta opción cuando `debug_ocr = true` está definido en TOML:

```powershell
--no-debug-ocr
```

Esto permite inspeccionar el texto OCR original y el texto limpiado antes de enviarlo al motor TTS.

## Voces

La aplicación expone cuatro perfiles de voz como nombres públicos estables:

| Nombre | Idioma | Género | Voz técnica (Edge TTS) |
| --- | --- | --- | --- |
| `Sofía` | Español (Bolivia) | Femenina | `es-BO-SofiaNeural` |
| `Elvira` | Español (España) | Femenina | `es-ES-ElviraNeural` |
| `Marcelo` | Español (Bolivia) | Masculina | `es-BO-MarceloNeural` |
| `Álvaro` | Español (España) | Masculina | `es-ES-AlvaroNeural` |

El usuario puede seleccionar una voz por su nombre público:

```powershell
python -m audiobook_generator.cli `
    --input "libro.pdf" `
    --output ".\output\libro" `
    --voice Álvaro
```

Los nombres públicos no distinguen mayúsculas/minúsculas ni acentos. Por ejemplo, `Álvaro`, `alvaro` y `ALVARO` resuelven al mismo perfil.

También se aceptan directamente los nombres técnicos de Edge TTS, manteniendo internamente el nombre público del perfil:

```powershell
--voice "es-ES-ElviraNeural"
```

También se mantienen los identificadores antiguos (`female_1`, `female_2`, `male_1`, `male_2`) como alias de compatibilidad.

### Catálogo de voces

Para consultar las voces disponibles sin iniciar una conversión:

```powershell
audiobook-generator --list-voices
```

El resultado muestra el nombre público, idioma, género y nombre técnico de Edge TTS. Esta salida también sirve como base para una futura interfaz gráfica.

## Velocidad

La velocidad puede modificarse mediante porcentajes:

```powershell
--rate "+10%"
```

o:

```powershell
--rate "-10%"
```

## Volumen

Ejemplo:

```powershell
--volume "+10%"
```

o:

```powershell
--volume "-5%"
```

## Tono

Ejemplo:

```powershell
--pitch "+2Hz"
```

o:

```powershell
--pitch "-4Hz"
```

## Fragmentación del texto

El texto se divide en fragmentos para evitar enviar bloques excesivamente grandes al motor TTS.

El tamaño máximo se controla mediante:

```powershell
--max-characters 3000
```

Por ejemplo:

```powershell
--max-characters 2000
```

El valor debe ser mayor que cero.

## Capítulos

El sistema puede identificar automáticamente encabezados de capítulos y otras estructuras similares.

Ejemplo:

```text
Capítulo 1

Texto del capítulo.

Capítulo 2

Texto del segundo capítulo.
```

También se reconocen variantes como:

```text
Chapter 1
Parte 1
Sección 1
```

Cuando un capítulo supera el límite máximo de caracteres, se divide automáticamente en partes para su procesamiento TTS.

## Capítulos individuales

Los capítulos pueden conservarse después de generar el audiolibro:

```powershell
python -m audiobook_generator.cli `
    --input "libro.pdf" `
    --output ".\output\libro" `
    --keep-chapters
```

El resultado tendrá una estructura similar a:

```text
output/
└── libro/
    ├── libro_Audiobook.mp3
    └── chapters/
        ├── CAPITULO_001.mp3
        ├── CAPITULO_002.mp3
        ├── CAPITULO_003.mp3
        └── ...
```

Para no conservar los capítulos individuales:

```powershell
--no-keep-chapters
```

Si la generación o la unión falla, los archivos temporales necesarios se conservan para facilitar el diagnóstico.

## Bitrate MP3

El bitrate se puede configurar mediante:

```powershell
--bitrate 128k
```

También se admiten valores como:

```text
128k
192k
256k
1M
```

El bitrate se transmite a FFmpeg mediante `-b:a`.

## FFmpeg

FFmpeg es necesario para generar el archivo MP3 final.

Los capítulos pueden generarse individualmente, pero el audiolibro final requiere que FFmpeg esté disponible en `PATH`.

Puede comprobarse mediante:

```powershell
ffmpeg -version
```

y:

```powershell
ffprobe -version
```

El archivo final se genera con un nombre similar a:

```text
libro_Audiobook.mp3
```

## Configuración TOML

El programa permite definir parámetros mediante un archivo TOML.

Ejemplo:

```toml
[tts]
voice = "Elvira"
rate = "+0%"
volume = "+0%"
pitch = "+0Hz"

[output]
format = "mp3"
bitrate = "160k"

[processing]
max_characters = 3000
temp_dir = "temp"
keep_chapters = true
```

Puede utilizarse mediante:

```powershell
python -m audiobook_generator.cli `
    --config ".\examples\audiobook.toml" `
    --input "libro.txt" `
    --output ".\output"
```

Las opciones proporcionadas explícitamente por CLI tienen prioridad sobre los valores definidos en el archivo TOML.

Por ejemplo:

```powershell
python -m audiobook_generator.cli `
    --config ".\examples\audiobook.toml" `
    --input "libro.txt" `
    --rate "+10%"
```

En este caso, `+10%` tiene prioridad sobre el valor `rate` definido en el TOML.

## Directorios de trabajo

Los archivos temporales se mantienen separados de los resultados finales.

Una ejecución puede producir una estructura similar a:

```text
temp/
└── libro/
    ├── fragmentos temporales
    └── archivos MP3 temporales

output/
└── libro/
    ├── libro_Audiobook.mp3
    └── chapters/
        ├── CAPITULO_001.mp3
        └── ...
```

Los directorios `output/` y `temp/` están excluidos del control de versiones.

## Testing

La suite automatizada se ejecuta mediante:

```powershell
python -m pytest -q
```

Estado de la versión `1.0.0`:

```text
202 passed, 1 skipped
```

El test omitido corresponde a la integración real:

```text
tests/test_integration_real.py
```

y está desactivado por defecto porque realiza una prueba utilizando servicios y herramientas reales.

### Integración real

Para ejecutarla:

```powershell
$env:RUN_REAL_INTEGRATION="1"
python -m pytest tests\test_integration_real.py -v
```

Esta prueba requiere:

* conexión funcional a Edge TTS;
* FFmpeg disponible en `PATH`.

Las pruebas unitarias normales no necesitan realizar llamadas de red.

## Verificación de versión

La versión actual puede consultarse mediante:

```powershell
python -m audiobook_generator.cli --version
```

Resultado esperado:

```text
audiobook-generator 1.0.0
```

## Estructura del proyecto

```text
Audiobook-Generator/
│
├── audiobook_generator/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   └── ffmpeg.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── config_loader.py
│   │   ├── errors.py
│   │   ├── models.py
│   │   ├── pipeline.py
│   │   ├── preprocessor.py
│   │   ├── splitter.py
│   │   └── voices.py
│   │
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── tesseract.py
│   │
│   ├── readers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── docx.py
│   │   ├── epub.py
│   │   ├── factory.py
│   │   ├── html.py
│   │   ├── odt.py
│   │   ├── pdf.py
│   │   ├── pdf_renderer.py
│   │   ├── rtf.py
│   │   └── text.py
│   │
│   └── tts/
│       ├── __init__.py
│       ├── base.py
│       └── edge.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── OCR.md
│   └── TESTING.md
│
├── examples/
│   ├── audiobook.toml
│   └── ...
│
├── tests/
│
├── .gitignore
├── pyproject.toml
├── README.md
├── requirements.txt
├── requirements-docs.txt
└── requirements-ocr.txt
```

## Estado del proyecto

**Audiobook Generator `1.0.0`** representa la primera versión funcional consolidada del proyecto.

El núcleo actual permite:

```text
Documento
    │
    ▼
Lectura
    │
    ▼
Preprocesamiento
    │
    ▼
Capítulos
    │
    ▼
Fragmentación
    │
    ▼
Text-to-Speech
    │
    ▼
MP3
    │
    ▼
FFmpeg
    │
    ▼
Audiolibro final
```

La arquitectura mantiene separados los lectores, procesamiento, OCR, TTS, audio y CLI, permitiendo ampliar posteriormente el proyecto sin acoplar la lógica de negocio a una interfaz gráfica.

La GUI será una capa adicional sobre este núcleo y no deberá duplicar la lógica existente.

## Próximas etapas

La versión `1.0.0` establece el núcleo funcional del proyecto.

Las siguientes etapas pueden centrarse en:

* interfaz gráfica;
* experiencia de usuario;
* selección visual de archivos;
* configuración de voz y parámetros TTS;
* progreso de generación;
* gestión visual de capítulos;
* reproducción y previsualización del audio;
* selección y administración de perfiles de voz;
* mejoras de diagnóstico y registro;
* incorporación de nuevos motores TTS en el futuro.

La arquitectura actual está preparada para que estas funciones se desarrollen sin reemplazar el pipeline existente.
