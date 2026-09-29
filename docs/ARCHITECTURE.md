# Arquitectura

## Flujo

```text
Input document
      |
      v
ReaderFactory
      |
      v
Document
      |
      v
Chapter splitter
      |
      v
TTS Engine
      |
      v
MP3 chapters
      |
      v
MP3 metadata
      |
      v
FFmpeg merger + chapter markers
      |
      v
Final audiobook
```

## Flujo específico para PDF

```text
PDF
 |
 v
PdfReader
 |
 +--> extracción de texto con pypdf
 |
 +--> ¿página con imagen y poco texto?
          |
          +--> no --> texto extraído
          |
          +--> sí --> PdfPageRenderer
                         |
                         v
                    OcrEngine
                         |
                         v
                    texto OCR
                         |
                         v
                    Document
```

El OCR se ejecuta por página para permitir documentos PDF mixtos, donde algunas
páginas contienen texto digital y otras contienen imágenes escaneadas.

## Componentes OCR

El sistema OCR está desacoplado mediante una interfaz `OcrEngine`.

Actualmente se proporciona:

- `OcrEngine`: interfaz del motor OCR.
- `TesseractOcrEngine`: implementación basada en Tesseract mediante `pytesseract`.
- `PdfPageRenderer`: interfaz para renderizar páginas PDF como imágenes.
- `PyMuPdfPageRenderer`: implementación basada en PyMuPDF.

El lector PDF coordina estos componentes, pero el motor OCR no conoce el
pipeline, el TTS ni la interfaz de usuario.

## Modos OCR

El comportamiento se controla mediante `OcrConfig`:

- `auto`: detecta páginas con imágenes y poco texto y aplica OCR solamente cuando es necesario.
- `always`: aplica OCR a todas las páginas del PDF.
- `never`: no ejecuta OCR; si el documento depende de páginas escaneadas, informa del problema.

## Reglas

1. La GUI no contiene lógica de negocio.
2. Los lectores no conocen el TTS.
3. El TTS no conoce la GUI.
4. El audio se procesa mediante componentes independientes.
5. Cada formato nuevo se incorpora mediante un reader.
6. Cada motor TTS nuevo implementa `TTSEngine`.
7. Cada motor OCR nuevo implementa `OcrEngine`.
8. El renderizado de páginas PDF se abstrae mediante `PdfPageRenderer`.
9. OCR es una capacidad opcional y no debe ser una dependencia obligatoria del procesamiento normal de PDF.
10. Los metadatos de audio se escriben mediante FFmpeg sin modificar el audio ya sintetizado.
11. Los marcadores de capítulo del MP3 final se generan a partir de las duraciones reales de los capítulos.
12. No crear archivos monolíticos para resolver nuevas funciones.
