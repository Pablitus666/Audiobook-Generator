class AudiobookError(Exception):
    """Error base controlado de la aplicación."""


class InputFileError(AudiobookError):
    """El archivo de entrada no puede leerse o no existe."""


class UnsupportedFormatError(AudiobookError, ValueError):
    """El formato del archivo no está soportado."""


class EmptyDocumentError(AudiobookError):
    """El documento no contiene texto utilizable."""


class DocumentReadError(AudiobookError):
    """Ocurrió un error al leer o extraer el contenido de un documento."""


class OcrError(DocumentReadError):
    """Ocurrió un error durante el procesamiento OCR."""


class OcrNotAvailableError(OcrError):
    """El motor OCR o sus dependencias no están disponibles."""


class TTSError(AudiobookError):
    """Ocurrió un error durante la síntesis de voz."""


class AudioMergeError(AudiobookError):
    """Ocurrió un error al unir los archivos de audio."""
