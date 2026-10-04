from pathlib import Path

from audiobook_generator.gui import main_window


def test_open_generated_folder_uses_parent_directory(monkeypatch, tmp_path):
    generated = tmp_path / "books" / "example_Audiobook.mp3"
    generated.parent.mkdir()
    generated.touch()

    opened = []
    monkeypatch.setattr(
        main_window.os,
        "startfile",
        lambda value: opened.append(value),
        raising=False,
    )

    window = object.__new__(main_window.MainWindow)
    window._open_generated_folder(generated)

    assert opened == [str(generated.parent.resolve())]


def test_asset_button_supports_custom_asset_filename():
    source = Path(main_window.__file__).resolve().parents[2] / "assets" / "images" / "boton1.png"
    widgets_source = source.parents[2] / "audiobook_generator" / "gui" / "widgets.py"
    text = widgets_source.read_text(encoding="utf-8")

    assert source.name == "boton1.png"
    assert 'asset_filename="boton.png"' in text
    assert "image_manager.load(asset_filename" in text
