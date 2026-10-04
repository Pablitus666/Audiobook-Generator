"""PyInstaller entry point for the Audiobook Generator GUI.

This launcher intentionally uses an absolute package import.  The GUI's
__main__.py uses a relative import, which is correct for ``python -m`` but
is not a valid PyInstaller script entry point when executed directly.
"""

from audiobook_generator.gui import run


if __name__ == "__main__":
    run()
