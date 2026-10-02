# Audiobook Generator

Aplicación modular para convertir documentos de texto en audiolibros MP3 mediante Text-to-Speech (TTS), con **CLI y una interfaz gráfica para Windows**.

**Versión:** `1.0.0`

## Características

* Conversión de documentos a audiolibros MP3.
* Arquitectura modular y desacoplada.
* Procesamiento por capítulos y fragmentos.
* Motor TTS basado en `edge-tts`.
* Cuatro perfiles de voz incluidos:
  * `Sofía` — `es-BO-SofiaNeural`
  * `Elvira` — `es-ES-ElviraNeural`
  * `Marcelo` — `es-BO-MarceloNeural`
  * `Álvaro` — `es-ES-AlvaroNeural`
* Configuración de velocidad, volumen y tono.
* División automática de contenido en capítulos.
* División de capítulos extensos en fragmentos para TTS.
* Unión de capítulos mediante FFmpeg.
* Conservación opcional de los capítulos MP3 individuales.
* Configuración mediante archivo TOML.
* Soporte OCR para documentos PDF escaneados.
* Modo de diagnóstico OCR.
* CLI disponible mediante `python -m audiobook_generator` y `audiobook-generator`.
* Interfaz gráfica disponible mediante `python -m audiobook_generator.gui` y `audiobook-generator-gui`.
* Detección automática del idioma de la interfaz, con soporte para español, inglés, alemán, francés, italiano, japonés, portugués, ruso y chino.
* Selección de documentos mediante explorador y arrastrar y soltar en Windows.
* Atajo `Enter` para iniciar la generación desde la ventana principal.
* Navegación por teclado mediante `Tab` y limpieza de rutas con `Backspace`/`Delete`.
* Barra de progreso y estado de generación en la GUI.
* Limpieza automática del directorio temporal `.audiobook_generator_temp` al finalizar cada trabajo.
* Diálogos visuales para advertencias, errores y generación completada.
* Limpieza automática de los campos de entrada y salida después de una generación completada.
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
* **GUI:** proporciona la interfaz gráfica sin duplicar la lógica del pipeline.

## Interfaz gráfica

La GUI está implementada con Tkinter y utiliza los mismos componentes de configuración y procesamiento que la CLI. Está especialmente orientada al uso en Windows.

La ventana principal permite:

* seleccionar el documento de entrada;
* arrastrar y soltar un documento compatible sobre el campo de entrada;
* seleccionar el directorio de salida;
* seleccionar voz, velocidad, volumen, tono y tamaño máximo de fragmento;
* activar o desactivar la conservación de capítulos;
* iniciar la generación;
* observar el porcentaje y estado del procesamiento;
* utilizar `Tab` para desplazarse entre los controles y `Enter` para generar;
* limpiar las rutas seleccionadas con `Backspace` o `Delete`.

Al completar correctamente una generación, la GUI reinicia el progreso y limpia los campos de entrada y salida para preparar el siguiente trabajo. El archivo generado y, si corresponde, la carpeta `chapters/` permanecen en el directorio de salida.

Durante el procesamiento se utiliza un directorio temporal oculto llamado `.audiobook_generator_temp`. La GUI lo elimina automáticamente al finalizar el trabajo, tanto después de una generación correcta como cuando se produce un error.

### Ejecutar la GUI

Desde el entorno virtual:

```powershell
python -m audiobook_generator.gui
```

También está disponible el comando instalado:

```powershell
audiobook-generator-gui
```

## Requisitos

### Software

* Python `3.10` o superior.
* FFmpeg disponible en `PATH`.
* Conexión a Internet para utilizar Edge TTS.

Para utilizar la interfaz gráfica se incluyen dependencias opcionales de GUI como `Pillow` y `tkinterdnd2`.

### TTS

El motor actual utiliza `edge-tts`, que actúa como cliente para el servicio de Text-to-Speech de Microsoft Edge.

Por lo tanto, la generación de audio requiere conectividad de red.

### GPU

La generación TTS actual **no requiere GPU**.

El procesamiento de texto, la división de capítulos y la comunicación con Edge TTS no utilizan una GPU local como requisito del proyecto.

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

Para instalar el paquete con las dependencias necesarias para desarrollo, GUI, documentación y OCR:

```powershell
python -m pip install -e ".[dev,gui,docs,ocr]"
```

La instalación de desarrollo incluye las herramientas de pruebas; `gui`, `docs` y `ocr` añaden las dependencias opcionales correspondientes.

### Dependencias de documentos

También pueden instalarse mediante:

```powershell
python -m pip install -r requirements-docs.txt
```

### OCR

Para habilitar el procesamiento OCR:

```powershell
python -m pip install -r requirements-ocr.txt
```

El OCR utiliza:

* PyMuPDF
* Tesseract
* Pillow

Además de las dependencias Python, Tesseract debe estar instalado y disponible para el sistema cuando se utilice OCR.

## Uso básico mediante CLI

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

Esto permite inspeccionar el texto OCR original y el texto limpiado antes de enviarlo al motor TTS.

## Voces

La aplicación dispone de cuatro perfiles de voz:

| Perfil | Idioma | Voz técnica |
|---|---|---|
| `Sofía` | Español (Bolivia) | `es-BO-SofiaNeural` |
| `Elvira` | Español (España) | `es-ES-ElviraNeural` |
| `Marcelo` | Español (Bolivia) | `es-BO-MarceloNeural` |
| `Álvaro` | Español (España) | `es-ES-AlvaroNeural` |

La CLI permite consultar el catálogo mediante:

```powershell
python -m audiobook_generator.cli --list-voices
```

También es posible utilizar directamente una voz compatible con Edge TTS:

```powershell
--voice "es-ES-ElviraNeural"
```

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
--max-characters 1500
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

La GUI ofrece el mismo comportamiento mediante el interruptor **Conservar capítulos**.

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

Puede utilizarse mediante:

```powershell
python -m audiobook_generator.cli `
    --config ".\examples\audiobook.toml" `
    --input "libro.txt" `
    --output ".\output"
```

Las opciones proporcionadas explícitamente por CLI tienen prioridad sobre los valores definidos en el archivo TOML.

## Directorios de trabajo

Los archivos temporales se mantienen separados de los resultados finales. En la GUI, el directorio temporal por ejecución es:

```text
.audiobook_generator_temp/
```

Este directorio se elimina automáticamente al terminar el trabajo de la GUI. En ejecuciones de CLI, el comportamiento de los archivos temporales depende de la configuración del pipeline y de la ejecución.

Una salida con capítulos conservados puede tener esta estructura:

```text
output/
└── libro/
    ├── libro_Audiobook.mp3
    └── chapters/
        ├── CAPITULO_001.mp3
        └── ...
```

## Testing

La suite automatizada se ejecuta mediante:

```powershell
python -m pytest -q
```

Validación actual del proyecto:

```text
226 passed, 1 skipped
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
│   ├── audio/
│   ├── core/
│   ├── gui/
│   ├── ocr/
│   ├── readers/
│   └── tts/
│
├── assets/
│   ├── fonts/
│   ├── images/
│   └── locales/
│
├── docs/
├── examples/
├── images/
├── tests/
│
├── .gitignore
├── pyproject.toml
├── README.md
├── RELEASE_DESCRIPTION.md
├── requirements.txt
├── requirements-docs.txt
└── requirements-ocr.txt
```

## Estado del proyecto

**Audiobook Generator `1.0.0`** es una versión funcional que reúne el núcleo de conversión, la CLI, OCR, configuración TOML y una interfaz gráfica de escritorio.

El flujo de generación es:

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

La GUI funciona como una capa de presentación sobre este núcleo: no duplica la lógica de lectura, procesamiento, TTS ni unión de audio.

## Próximas etapas

Las siguientes etapas pueden centrarse en:

* mejoras de experiencia de usuario;
* reproducción y previsualización del audio;
* gestión visual más avanzada de capítulos;
* mejoras de diagnóstico y registro;
* incorporación de nuevos motores TTS en el futuro;
* empaquetado y distribución independiente para Windows, incluido un posible instalador `.exe`.

## Licencia

Audiobook Generator se distribuye bajo la licencia **MIT**.
