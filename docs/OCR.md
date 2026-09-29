# OCR de PDF

Audiobook Generator puede procesar PDF que contienen páginas escaneadas o imágenes sin texto extraíble. El OCR es una función opcional y utiliza Tesseract para convertir esas imágenes en texto antes de continuar con el pipeline normal.

## Modos

- `auto`: detecta páginas con poco o ningún texto extraíble y aplica OCR solamente a esas páginas. Es el modo recomendado.
- `always`: fuerza OCR en todas las páginas del PDF.
- `never`: desactiva OCR y utiliza únicamente la extracción normal de texto.

Ejemplo:

```powershell
audiobook-generator --input libro.pdf --ocr auto --ocr-language spa
```

## Dependencias

Instala las dependencias Python de OCR:

```powershell
pip install -r requirements-ocr.txt
```

También es necesario instalar Tesseract OCR y hacer que el ejecutable `tesseract` esté disponible en `PATH`.

## Idioma, resolución y segmentación

La configuración predeterminada es:

- idioma: `spa`
- resolución: `300` DPI
- PSM de Tesseract: `3`

Se pueden modificar desde la CLI:

```powershell
audiobook-generator `
    --input libro.pdf `
    --ocr auto `
    --ocr-language spa+eng `
    --ocr-dpi 300 `
    --ocr-psm 3
```

También pueden configurarse mediante TOML:

```toml
[ocr]
mode = "auto"
language = "spa"
dpi = 300
psm = 3
```

## Limitaciones

OCR no garantiza una transcripción perfecta. La precisión depende de la resolución y calidad del escaneo, tipografía, orientación, contraste, idioma y diseño de la página. Tablas, formularios, sellos, firmas, columnas complejas y otros elementos gráficos pueden producir resultados incorrectos o incompletos.

Por este motivo, el OCR debe considerarse una función de compatibilidad para hacer procesables determinados PDF, no un sustituto de una revisión humana cuando la fidelidad del texto sea importante.

La limpieza posterior es deliberadamente conservadora: corrige o elimina algunos artefactos evidentes, pero no realiza corrección ortográfica general ni reescribe el contenido.

## Diagnóstico

Para inspeccionar el resultado de OCR antes de enviarlo al TTS:

```powershell
audiobook-generator `
    --input libro.pdf `
    --output output\ocr_debug `
    --debug-ocr
```

Cuando se utiliza OCR, el directorio de diagnóstico contiene:

- `original_ocr.txt`: texto producido por Tesseract antes de la limpieza.
- `cleaned_ocr.txt`: texto después de la limpieza OCR y antes de dividir capítulos y generar audio.

Estos archivos se generan solamente cuando se utiliza `--debug-ocr`.
