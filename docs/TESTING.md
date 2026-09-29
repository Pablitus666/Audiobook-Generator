# Testing

El proyecto debe poder probar su lógica principal sin depender de servicios TTS
externos ni de una instalación funcional de FFmpeg.

## Suite

La suite automatizada cubre las principales capas del proyecto:

* `test_factory.py`: selección del lector según la extensión del archivo.
* `test_readers.py`: lectura de documentos de texto y comportamiento general de los lectores.
* `test_epub.py`: lectura de archivos EPUB y extracción de capítulos.
* `test_splitter.py`: detección y división de capítulos.
* `test_preprocessor.py`: limpieza y preparación del texto antes del TTS.
* `test_cli.py`: argumentos y valores predeterminados de la CLI.
* `test_cli_config.py`: configuración mediante archivo TOML.
* `test_cli_config_precedence.py`: prioridad de argumentos de CLI sobre la configuración.
* `test_config.py`: configuración del proyecto.
* `test_config_loader.py`: carga de configuración.
* `test_config_loader_validation.py`: validación de configuración.
* `test_audio.py`: comportamiento del módulo FFmpeg.
* `test_ffmpeg_metadata.py`: metadatos de los archivos de audio.
* `test_pipeline.py`: pipeline completo utilizando componentes falsos.
* `test_pipeline_keep_chapters.py`: generación y conservación de capítulos.
* `test_tts.py`: comportamiento de la interfaz y motor TTS.
* `test_voices.py`: perfiles de voz disponibles.
* `test_integration.py`: integración entre los componentes principales.
* `test_integration_real.py`: pruebas que utilizan servicios y herramientas reales.
* `test_version.py`: versión declarada del proyecto.

## Pruebas unitarias

Las pruebas unitarias no deben realizar llamadas de red ni depender de servicios
externos.

Cuando sea necesario probar componentes como TTS o FFmpeg, las pruebas
unitarias deben utilizar implementaciones falsas, mocks o componentes
controlados por las pruebas.

Esto permite ejecutar la suite de forma reproducible sin necesidad de una
conexión a Internet ni de un entorno externo completamente configurado.

## Pruebas de integración real

Las pruebas de integración real se mantienen separadas de las pruebas
unitarias.

Estas pruebas pueden requerir:

* conexión a Internet;
* Microsoft Edge TTS disponible;
* FFmpeg instalado y accesible mediante `PATH`;
* archivos de ejemplo disponibles.

Su objetivo es verificar que los componentes funcionan correctamente cuando se
ejecuta el flujo real de generación de audiolibros.

## Formatos de entrada

Los lectores actualmente cubiertos por el proyecto incluyen:

* TXT
* Markdown
* PDF
* DOCX
* EPUB
* RTF
* HTML
* XHTML
* ODT

Los lectores EPUB, RTF, HTML/XHTML y ODT utilizan implementaciones basadas en
la biblioteca estándar de Python.

PDF y DOCX utilizan sus dependencias opcionales correspondientes.

## Ejecutar la suite

Para ejecutar todas las pruebas:

```powershell
pytest -q
```

Para ejecutar un archivo específico:

```powershell
pytest tests\test_epub.py -q
```

Para obtener información adicional:

```powershell
pytest -ra
```

## Verificación actual

La suite automatizada debe ejecutarse en el entorno virtual del proyecto con:

```powershell
python -m pytest -q
```

El número de pruebas puede variar conforme se añaden nuevas comprobaciones. La
prueba de integración real permanece desactivada por defecto porque requiere
servicios y herramientas externas.

La prueba omitida corresponde a la integración real, desactivada por defecto porque requiere servicios y herramientas externas.

Además de la suite automatizada, se ha verificado el flujo real de generación
de audiolibros utilizando archivos de ejemplo en formatos TXT, PDF, EPUB, RTF,
HTML y ODT.

Estas pruebas reales verifican la interacción entre lectura del documento,
preprocesamiento, división en capítulos, TTS y generación del audio final.

## Principios

Las pruebas deben:

1. Ser reproducibles.
2. Evitar dependencias externas en las pruebas unitarias.
3. Mantener separadas las pruebas unitarias de las pruebas de integración real.
4. Cubrir los lectores y componentes principales.
5. Verificar el comportamiento del pipeline sin acoplar las pruebas a una
   implementación concreta cuando no sea necesario.


## OCR

Las pruebas OCR deben separar la lógica del lector de la implementación concreta
de Tesseract.

Las pruebas unitarias utilizan motores OCR y renderizadores falsos para comprobar:

- detección automática de páginas escaneadas;
- procesamiento de PDFs mixtos;
- modo `always`;
- modo `never`;
- propagación de errores cuando OCR no está disponible.

Las pruebas que utilizan Tesseract real deben mantenerse separadas de la suite
unitaria y depender de una instalación funcional de Tesseract.
