"""Windows DPI awareness helpers used only for image rendering.

The GUI deliberately does not change Tk's global scaling factor. Fonts,
widget geometry and spacing remain at their existing application sizes; the
DPI factor is passed only to ImageManager so raster assets can be rendered at
higher physical resolution.
"""


def enable_dpi_awareness() -> None:
    """Enable Windows DPI awareness before creating any Tk window."""
    import ctypes

    if not hasattr(ctypes, "WinDLL"):
        return

    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def get_tkinter_scalefactor(window) -> float:
    """Return the display DPI factor relative to the 96-DPI Windows base.

The returned value is consumed by ImageManager only; it must not be applied
through ``tk scaling`` because that would change fonts and widget geometry.
"""
    try:
        dpi = window.winfo_fpixels("1i")
        scale = float(dpi) / 96.0
        return scale if scale > 1.0 else 1.0
    except Exception:
        return 1.0
