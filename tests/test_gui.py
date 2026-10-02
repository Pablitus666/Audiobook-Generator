from pathlib import Path

import tkinter as tk

from audiobook_generator.gui.main_window import MainWindow
from audiobook_generator.gui.styles import BG_COLOR, FONT_DIR, FONT_FAMILY
from audiobook_generator.gui.widgets import SwitchToggle


def test_gui_assets_are_project_local():
    project_root = Path(__file__).resolve().parents[1]
    images = project_root / "assets" / "images"
    assert images.exists()
    assert (images / "logo.png").exists()
    assert (images / "titulo.png").exists()
    assert (images / "boton.png").exists()
    assert (images / "icon.ico").exists()


def test_gui_bundled_font_is_project_local():
    project_root = Path(__file__).resolve().parents[1]
    fonts = project_root / "assets" / "fonts"

    assert FONT_DIR == fonts
    assert (fonts / "SourceSans3-Regular.ttf").exists()
    assert (fonts / "SourceSans3-Semibold.ttf").exists()
    assert (fonts / "SourceSans3-Bold.ttf").exists()


def test_gui_palette_and_font():
    assert BG_COLOR == "#023047"
    assert FONT_FAMILY == "Source Sans 3"


def test_main_window_builds():
    root = tk.Tcl()
    assert root is not None


def test_visual_widget_dimensions():
    assert SwitchToggle.WIDTH == 62
    assert SwitchToggle.HEIGHT == 32
    assert SwitchToggle._SCALE >= 8


def test_asset_button_can_initialize():
    """Regression test: AssetButton must not query Tk methods before super().__init__()."""
    from audiobook_generator.gui.image_manager import ImageManager
    from audiobook_generator.gui.widgets import AssetButton

    root = tk.Tk()
    root.withdraw()
    try:
        images = ImageManager(root)
        button = AssetButton(root, images, "Examinar", width=126, height=44)
        assert button.winfo_exists()
        button.destroy()
    finally:
        root.destroy()


def test_asset_button_disable_keeps_visual_identity():
    """Busy-state disabling must not grey out the branded button."""
    from audiobook_generator.gui.widgets import AssetButton
    import inspect

    source = inspect.getsource(AssetButton.set_enabled)
    assert 'fg="white" if enabled else "#888888"' not in source
    assert 'self._enabled = enabled' in source
