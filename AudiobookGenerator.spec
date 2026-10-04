from pathlib import Path

from PyInstaller.utils.hooks import collect_all


ROOT = Path(SPECPATH)


# ---------------------------------------------------------------------------
# Project resources
# ---------------------------------------------------------------------------

datas = [
    (str(ROOT / "assets"), "assets"),
]


# ---------------------------------------------------------------------------
# tkinterdnd2
# ---------------------------------------------------------------------------

tdnd_datas, tdnd_binaries, tdnd_hiddenimports = collect_all("tkinterdnd2")
datas += tdnd_datas


# ---------------------------------------------------------------------------
# Edge TTS
# ---------------------------------------------------------------------------

edge_datas, edge_binaries, edge_hiddenimports = collect_all("edge_tts")
datas += edge_datas


# ---------------------------------------------------------------------------
# PyMuPDF
# ---------------------------------------------------------------------------

try:
    pymupdf_datas, pymupdf_binaries, pymupdf_hiddenimports = collect_all(
        "pymupdf"
    )
    datas += pymupdf_datas
except Exception:
    pymupdf_binaries = []
    pymupdf_hiddenimports = []


# ---------------------------------------------------------------------------
# Hidden imports
# ---------------------------------------------------------------------------

hiddenimports = [
    # GUI
    "tkinterdnd2",
    "audiobook_generator.gui",
    "audiobook_generator.gui.__init__",
    "audiobook_generator.gui.main_window",
    "audiobook_generator.gui.about_window",
    "audiobook_generator.gui.image_enhancer",
    "audiobook_generator.gui.image_manager",
    "audiobook_generator.gui.styles",
    "audiobook_generator.gui.widgets",

    # TTS
    "edge_tts",
    "audiobook_generator.tts.base",
    "audiobook_generator.tts.edge",

    # Audio
    "audiobook_generator.audio.ffmpeg",

    # Core
    "audiobook_generator.core.config",
    "audiobook_generator.core.config_loader",
    "audiobook_generator.core.dpi",
    "audiobook_generator.core.errors",
    "audiobook_generator.core.locale_utils",
    "audiobook_generator.core.localization",
    "audiobook_generator.core.models",
    "audiobook_generator.core.pipeline",
    "audiobook_generator.core.preprocessor",
    "audiobook_generator.core.splitter",
    "audiobook_generator.core.voices",

    # OCR
    "audiobook_generator.ocr.base",
    "audiobook_generator.ocr.tesseract",

    # Readers
    "audiobook_generator.readers.base",
    "audiobook_generator.readers.docx",
    "audiobook_generator.readers.epub",
    "audiobook_generator.readers.factory",
    "audiobook_generator.readers.html",
    "audiobook_generator.readers.odt",
    "audiobook_generator.readers.pdf",
    "audiobook_generator.readers.pdf_renderer",
    "audiobook_generator.readers.rtf",
    "audiobook_generator.readers.text",

    # Third-party document libraries
    "pypdf",
    "docx",
    "pymupdf",
    "pytesseract",
]

hiddenimports += tdnd_hiddenimports
hiddenimports += edge_hiddenimports
hiddenimports += pymupdf_hiddenimports


# ---------------------------------------------------------------------------
# Binaries
# ---------------------------------------------------------------------------

binaries = []
binaries += tdnd_binaries
binaries += edge_binaries
binaries += pymupdf_binaries


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
#
# IMPORTANT:
# Do NOT use audiobook_generator/gui/__main__.py directly here.
# That file contains a relative import:
#
#     from .main_window import run
#
# PyInstaller executes the script entry point as a top-level script, so that
# relative import has no package parent and fails.
#
# build_launcher.py uses:
#
#     from audiobook_generator.gui import run
#
# which is a valid absolute package import and preserves the exact same GUI
# entry point.
# ---------------------------------------------------------------------------

a = Analysis(
    [
        str(ROOT / "build_launcher.py"),
    ],
    pathex=[
        str(ROOT),
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "pytest_asyncio",
        "reportlab",
    ],
    noarchive=False,
)


# ---------------------------------------------------------------------------
# PYZ
# ---------------------------------------------------------------------------

pyz = PYZ(a.pure)


# ---------------------------------------------------------------------------
# SINGLE-FILE EXECUTABLE
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AudiobookGenerator",

    # Windowed application
    console=False,
    disable_windowed_traceback=False,

    # Debugging
    debug=False,
    bootloader_ignore_signals=False,

    # Optimization / compression
    strip=False,
    upx=False,

    # -----------------------------------------------------------------------
    # EXE ICON
    # -----------------------------------------------------------------------
    #
    # icon.ico is the dedicated executable icon.
    # It is separate from loguito.ico, which is used by the running GUI.
    #
    icon=str(
        ROOT / "assets" / "images" / "icon.ico"
    ),
)