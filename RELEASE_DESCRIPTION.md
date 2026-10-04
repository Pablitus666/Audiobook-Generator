🎙️ Audiobook Generator

🚀 Audiobook Generator 1.0.0

Audiobook Generator is a Windows desktop application for turning books and other documents into MP3 audiobooks using Microsoft Edge TTS.

The project combines document extraction, chapter detection, text cleanup, optional OCR, text-to-speech generation and audio assembly into a single workflow. It provides both a graphical interface for everyday use and a CLI for automation and advanced workflows.

✨ What makes Audiobook Generator useful?

Audiobook Generator is designed to take a document and handle most of the work required to transform it into a listenable audiobook:

📄 Reads multiple document formats.

📚 Detects and processes chapters automatically.

✂️ Splits long chapters into TTS-compatible fragments.

🧠 Uses OCR when a PDF contains scanned pages.

🔊 Generates speech through Microsoft Edge TTS.

🎛️ Lets you control voice, speed, volume and pitch.

🎧 Produces MP3 audio and can optionally preserve individual chapter files.

🏷️ Adds audiobook metadata and chapter navigation information to the generated audio.

🖥️ Provides a Windows GUI with drag-and-drop support.

⌨️ Supports keyboard-oriented workflows.

🌐 Provides a localized interface with language handling suitable for Windows users.

⚙️ Supports TOML configuration for repeatable workflows.

🧹 Manages temporary processing files automatically.

The goal is not simply to convert text to speech, but to provide a complete document-to-audiobook workflow.

🖥️ Windows application

Audiobook Generator is primarily designed for Windows.

The application can be used from source with Python or distributed as a standalone Windows executable. The release build is packaged with PyInstaller, so the end user does not need to install Python just to run the packaged application.

The graphical interface includes:

Document selection

Drag and drop

Output directory selection

Voice selection

Speech speed, volume and pitch controls

Maximum fragment size

Optional chapter preservation

OCR controls

Progress and processing status

Keyboard navigation

Input validation and user feedback

The application also handles temporary processing data automatically through:

.audiobook_generator_temp/

📄 Supported input formats

Audiobook Generator can process:

TXT

PDF

DOCX

EPUB

HTML

ODT

RTF

Markdown

PDF documents can additionally be processed through the OCR pipeline when their content is image-based or otherwise requires text recognition.

🧠 OCR

The OCR pipeline is intended primarily for scanned PDF documents.

It supports three operating modes:

auto
always
never

It also provides configuration for:

--ocr-language "spa"
--ocr-dpi 300
--ocr-psm 6

Multiple OCR languages can be selected, for example:

--ocr-language "spa+eng"

For troubleshooting and diagnostics:

--debug-ocr

The OCR workflow integrates PyMuPDF, Tesseract and Pillow, with processing intended to reduce common OCR noise before the text reaches the audiobook pipeline.

🔊 Text-to-Speech

Audiobook Generator uses Microsoft Edge TTS for speech synthesis.

The application includes Spanish voice profiles such as:

Profile

Language

Technical voice

Sofía

Spanish (Bolivia)

es-BO-SofiaNeural

Elvira

Spanish (Spain)

es-ES-ElviraNeural

Marcelo

Spanish (Bolivia)

es-BO-MarceloNeural

Álvaro

Spanish (Spain)

es-ES-AlvaroNeural

The available Edge TTS catalog can also be queried through the CLI:

python -m audiobook_generator.cli --list-voices

An Internet connection is required for Edge TTS generation.

🎛️ Audio controls

Speech generation can be customized through the GUI, CLI or TOML configuration.

Speed

--rate "+10%"

Volume

--volume "+10%"

Pitch

--pitch "+2Hz"

Maximum fragment size

--max-characters 1500

Long chapters are automatically divided into smaller fragments so they can be processed safely by the TTS pipeline.

📚 Chapters and audiobook output

Audiobook Generator detects chapter structures in supported documents and processes them as separate logical sections.

A long chapter can be divided into multiple TTS fragments while remaining part of the same chapter.

When requested, individual chapter MP3 files can also be retained:

--keep-chapters

The final audiobook can include metadata and chapter navigation information, making it easier to move between sections when the player supports those features.

🌐 Localization

The GUI includes localization support and can adapt its language according to the configured environment.

The project includes localized resources under the application assets, while the application also allows the language to be controlled explicitly when required.

This makes the same application suitable for users working in different Windows language environments.

⚙️ Configuration

Audiobook Generator supports TOML configuration files so that frequently used settings can be stored and reused.

Example:

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

Command-line options take precedence over values supplied by the TOML configuration.

This makes it possible to maintain a preferred configuration while still overriding individual options for a particular audiobook.

🚀 Using the application

Graphical interface

From a development environment:

python -m audiobook_generator.gui

The installed Python package also provides:

audiobook-generator-gui

For normal Windows users, the preferred distribution method is the packaged application available through the project's releases.

CLI

A basic example:

python -m audiobook_generator.cli `
    --input "libro.txt" `
    --output ".\output"

To view all available options:

python -m audiobook_generator.cli --help

The CLI uses the same processing core as the GUI, making it suitable for scripted and repeatable workflows.

🛠️ Development

Create a virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install the project and development dependencies:

python -m pip install -e ".[dev,gui,docs,ocr]"

The project separates the graphical interface, command-line interface, document readers, OCR, TTS integration, audio processing and core pipeline so that individual components can be tested and maintained independently.

🧪 Testing

The project includes an automated test suite covering the main processing components.

Run the standard suite with:

python -m pytest -q

The 1.0.0 development cycle reached:

226 passed, 1 skipped

The skipped test corresponds to the real integration workflow, which is disabled by default.

It can be executed with:

$env:RUN_REAL_INTEGRATION="1"
python -m pytest tests\test_integration_real.py -v

📦 Requirements

For development or execution from source:

Python 3.10 or newer

FFmpeg available in PATH

Internet connection for Edge TTS

Tesseract for OCR functionality

The standalone Windows release packages the application so that Python does not need to be installed separately by the end user.

📦 Distribution

Audiobook Generator 1.0.0 is distributed as a Windows application.

The release workflow uses:

PyInstaller for the standalone executable

Inno Setup for the Windows installer

The repository contains the source code and project files; generated release binaries and local signing materials are kept outside the source repository and published separately through the project's release distribution.

✅ Version 1.0.0

Version 1.0.0 represents the first complete release of Audiobook Generator.

The release includes:

✔️ Windows GUI

✔️ CLI

✔️ Drag-and-drop document input

✔️ Multiple document formats

✔️ Chapter detection and processing

✔️ Automatic chapter fragmentation

✔️ Edge TTS integration

✔️ Voice, speed, volume and pitch controls

✔️ OCR pipeline for scanned PDFs

✔️ TOML configuration

✔️ Localized interface

✔️ Temporary-file management

✔️ Optional chapter MP3 preservation

✔️ Audiobook metadata and chapter navigation

✔️ Automated test suite

✔️ Standalone Windows executable

✔️ Windows installer

📄 License

This project is distributed under the MIT License.

👨‍💻 Author

Walter Pablo Téllez Ayala

Software Developer

📍 Bolivia 🇧🇴

📧 pharmakoz@gmail.com

© 2026 — Audiobook Generator