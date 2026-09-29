from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REAL_INTEGRATION") != "1",
    reason=(
        "Prueba de integración real desactivada. "
        "Ejecutar con RUN_REAL_INTEGRATION=1."
    ),
)


def test_real_integration_txt_tts_ffmpeg(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    source = project_root / "examples" / "ejemplo.txt"

    if not source.exists():
        pytest.fail(f"No existe el archivo de prueba: {source}")

    if shutil.which("ffmpeg") is None:
        pytest.fail(
            "FFmpeg no está disponible en PATH. "
            "La prueba real necesita FFmpeg."
        )

    output_dir = tmp_path / "output"
    temp_dir = tmp_path / "temp"

    command = [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "audiobook_generator",
        "--input",
        str(source),
        "--output",
        str(output_dir),
        "--temp-dir",
        str(temp_dir),
        "--voice",
        "Elvira",
        "--keep-chapters",
    ]

    completed = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert completed.returncode == 0, (
        "La generación real del audiolibro falló.\n\n"
        f"STDOUT:\n{completed.stdout}\n\n"
        f"STDERR:\n{completed.stderr}"
    )

    merged_file = output_dir / "ejemplo_Audiobook.mp3"
    chapters_dir = output_dir / "chapters"
    temp_book_dir = temp_dir / "ejemplo"

    assert merged_file.exists()
    assert merged_file.stat().st_size > 0

    chapter_files = sorted(chapters_dir.glob("CAPITULO_*.mp3"))

    assert chapter_files
    assert all(
        path.stat().st_size > 0
        for path in chapter_files
    )

    assert not temp_book_dir.exists()
