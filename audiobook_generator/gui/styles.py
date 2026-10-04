"""Centralized visual style for the Audiobook Generator GUI.

The GUI uses the bundled Source Sans 3 font from the project-level
``assets/fonts`` directory. On Windows the TTF files are registered as
process-private fonts, so the application does not depend on a Microsoft
font being installed and does not permanently install the bundled font
in Windows.

The visual language is intentionally dark: deep blue/petrol surfaces,
dark input fields, cyan interaction states, and a restrained warm-yellow
accent.
"""

from pathlib import Path
import sys
from tkinter import ttk
import tkinter as tk

FONT_FAMILY = "Source Sans 3"
FONT_FALLBACK_FAMILY = "TkDefaultFont"

# ---------------------------------------------------------------------------
# Audiobook Generator visual identity
# ---------------------------------------------------------------------------

BG_COLOR = "#023047"
PANEL_BG = "#06394A"

ACCENT_COLOR = "#FCBF49"
TEXT_COLOR = "white"
SECONDARY_TEXT_COLOR = "#A1D6E2"

# Dark controls: integrated with the application instead of using the
# default Windows/Tk white fields.
FIELD_BG = "#082B36"
FIELD_FG = "#FFFFFF"
FIELD_BORDER = "#14566A"
FIELD_FOCUS = "#219EBC"
FIELD_FOCUS_BG = "#0B3542"

WIDGET_DARK = "#1B1B1B"
WIDGET_HOVER = "#2A2A2A"
MEDIA_BG = "#0B2027"

# Project layout:
#   <project root>/assets/fonts/*.ttf
#   <project root>/audiobook_generator/gui/styles.py
#
# parents[0] = gui
# parents[1] = audiobook_generator
# parents[2] = project root
FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

FONT_FILES = (
    "SourceSans3-Regular.ttf",
    "SourceSans3-Semibold.ttf",
    "SourceSans3-Bold.ttf",
)

# Keep successful registrations alive for the lifetime of the process.
_registered_font_paths: list[Path] = []

# Keep the custom Combobox arrow image alive for the lifetime of the process.
_combobox_arrow_photo: tk.PhotoImage | None = None


def _register_bundled_fonts() -> bool:
    """Register bundled TTF files privately for the current Windows process.

    FR_PRIVATE makes the fonts available to this process without installing
    them into the user's Windows font collection.
    """
    if not sys.platform.startswith("win"):
        return False

    try:
        import ctypes
        from ctypes import wintypes

        add_font = ctypes.windll.gdi32.AddFontResourceExW
        add_font.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.LPVOID,
        ]
        add_font.restype = wintypes.INT

        FR_PRIVATE = 0x10
        registered_any = False

        for filename in FONT_FILES:
            path = FONT_DIR / filename
            if not path.is_file():
                continue

            if path in _registered_font_paths:
                registered_any = True
                continue

            if add_font(str(path), FR_PRIVATE, None) > 0:
                _registered_font_paths.append(path)
                registered_any = True

        if registered_any:
            # Notify Windows that the process font collection changed so Tk
            # can discover the newly registered private family.
            try:
                user32 = ctypes.windll.user32
                HWND_BROADCAST = 0xFFFF
                WM_FONTCHANGE = 0x001D
                SMTO_ABORTIFHUNG = 0x0002
                result = wintypes.DWORD()

                user32.SendMessageTimeoutW(
                    HWND_BROADCAST,
                    WM_FONTCHANGE,
                    0,
                    0,
                    SMTO_ABORTIFHUNG,
                    1000,
                    ctypes.byref(result),
                )
            except Exception:
                # Font registration itself succeeded; notification is only
                # a convenience for Tk discovery.
                pass

        return registered_any

    except Exception:
        # The GUI can still run with Tk's default font if private registration
        # is unavailable on a particular Windows/Tk build.
        return False


def resolve_font_family(root: object) -> str:
    """Return Source Sans 3 when the bundled font is available.

    If the bundled files cannot be registered/discovered, use Tk's generic
    default instead of falling back to a Microsoft-specific font.
    """
    _register_bundled_fonts()

    try:
        import tkinter.font as tkfont

        families = set(tkfont.families(root))
        if FONT_FAMILY in families:
            return FONT_FAMILY
    except Exception:
        pass

    return FONT_FALLBACK_FAMILY


def _make_white_combobox_arrow(root: object) -> tk.PhotoImage:
    """Create a small native-Tk white down arrow.

    ttk's ``arrowcolor`` option is theme dependent and is not honored
    consistently by every Windows Tk/ttk build.  A tiny image element is
    deterministic: it remains white in normal, focus, active and pressed
    states without replacing the native Combobox mouse/keyboard behavior.
    """
    photo = tk.PhotoImage(master=root, width=11, height=8)

    # PhotoImage starts transparent.  Draw a compact centered triangle.
    rows = (
        "     ",
        "     ",
        "#####",
        " ####",
        "  ###",
        "   #",
    )
    for y, row in enumerate(rows):
        x0 = 3
        for x, char in enumerate(row):
            if char == "#":
                photo.put(TEXT_COLOR, to=(x0 + x, y + 1))

    return photo


def _replace_layout_element(layout: object, old: str, new: str) -> object:
    """Recursively replace one ttk layout element name."""
    if isinstance(layout, (list, tuple)):
        if len(layout) == 2 and isinstance(layout[0], str) and isinstance(layout[1], dict):
            name, options = layout
            copied = dict(options)
            if "children" in copied:
                copied["children"] = _replace_layout_element(copied["children"], old, new)
            if name == old:
                name = new
            return (name, copied)

        return type(layout)(
            _replace_layout_element(item, old, new)
            for item in layout
        )

    return layout


def _install_combobox_arrow(style: ttk.Style, root: object) -> None:
    """Replace the theme's down-arrow element with a fixed white arrow."""
    global _combobox_arrow_photo

    if _combobox_arrow_photo is None:
        _combobox_arrow_photo = _make_white_combobox_arrow(root)

    try:
        style.element_create(
            "AG.DownArrow",
            "image",
            _combobox_arrow_photo,
            border=0,
            sticky="",
        )
    except tk.TclError:
        # The element may already exist if styles are configured more than
        # once during an interactive session.  Reusing it is safe.
        pass

    try:
        layout = style.layout("TCombobox")
        layout = _replace_layout_element(
            layout,
            "Combobox.downarrow",
            "AG.DownArrow",
        )
        style.layout("AG.TCombobox", layout)
    except (tk.TclError, TypeError, ValueError):
        # The normal ttk arrow remains available as a safe fallback.
        pass


def _style_combobox_popdown(combobox: object) -> None:
    """Apply the dark palette and spacing to ttk's real popup Listbox.

    ttk creates the popup lazily.  The popup is a native Tk toplevel containing
    a Listbox and scrollbar, so styling it through ``nametowidget`` during
    Combobox construction is unsafe on some Python/Tk builds.  Tcl gives us
    the exact widget path after it exists, which avoids the previous
    ``KeyError: 'popdown'`` startup failure.

    The Listbox is given horizontal grid padding.  This is the correct way to
    create the visual "air" requested around the option text without changing
    the actual values stored in the Combobox.
    """
    try:
        root = combobox.winfo_toplevel()
        popdown = root.tk.call("ttk::combobox::PopdownWindow", combobox._w)
        listbox = f"{popdown}.f.l"
        scrollbar = f"{popdown}.f.sb"
        frame = f"{popdown}.f"

        # Popup container.
        try:
            root.tk.call(frame, "configure", "-style", "ComboboxPopdownFrame")
        except tk.TclError:
            pass

        # The ttk popup uses a real Tk Listbox.  Keep the selected row
        # visually identical to the normal row, while retaining native
        # selection semantics so mouse/keyboard interaction remains intact.
        root.tk.call(
            listbox,
            "configure",
            "-background", FIELD_BG,
            "-foreground", FIELD_FG,
            "-selectbackground", FIELD_BG,
            "-selectforeground", FIELD_FG,
            "-highlightbackground", FIELD_BORDER,
            "-highlightcolor", FIELD_BORDER,
            "-highlightthickness", 0,
            "-borderwidth", 0,
            "-relief", "flat",
            "-activestyle", "none",
            "-font", (getattr(root, "font_family", FONT_FAMILY), 10),
        )

        # Add breathing room at the left/right edges of the popup.  Listbox
        # itself has no item-padding option; grid padding is the native,
        # non-invasive way to achieve it.
        root.tk.call(
            "grid", "configure", listbox,
            "-padx", "8 8",
            "-pady", "2 2",
        )

        # Hide the popup scrollbar. The option list is short and the native
        # scrollbar only adds visual noise in this interface.
        try:
            root.tk.call("grid", "forget", scrollbar)
        except tk.TclError:
            pass

        # Match the popup to the application palette.
        try:
            root.tk.call(
                popdown,
                "configure",
                "-background", FIELD_BG,
                "-borderwidth", 0,
                "-highlightthickness", 0,
            )
        except tk.TclError:
            pass

    except (tk.TclError, AttributeError, TypeError):
        # The popup is created lazily.  If it does not exist yet, the next
        # scheduled restyle will try again; never interfere with opening it.
        pass


def _clear_combobox_selection(combobox: object) -> None:
    """Remove the native text-selection highlight without stealing focus.

    Tk/Windows can leave the current value painted as selected after opening
    or choosing a readonly ttk.Combobox.  Clearing the selection is purely
    visual; it does not change the associated StringVar or the Combobox value.
    """
    try:
        combobox.selection_clear()
    except (tk.TclError, AttributeError):
        pass


def prepare_combobox(combobox: object) -> object:
    """Prepare a ttk.Combobox while preserving native one-click behavior.

    The popup is styled only after ttk has created it.  No class bindings are
    replaced and no synthetic click is generated, so the native arrow remains
    a normal one-click control.
    """

    def restyle(cb=combobox) -> None:
        try:
            # PopdownWindow may not exist at ButtonPress time.  Both callbacks
            # run after Tk has had a chance to create it.
            cb.after_idle(lambda: _style_combobox_popdown(cb))
            cb.after(40, lambda: _style_combobox_popdown(cb))
        except (tk.TclError, AttributeError):
            pass

    try:
        combobox.bind("<ButtonPress-1>", lambda _e: restyle(), add="+")
        combobox.bind("<ButtonRelease-1>", lambda _e: restyle(), add="+")
        combobox.bind("<FocusIn>", lambda _e: restyle(), add="+")
        combobox.bind(
            "<<ComboboxSelected>>",
            lambda _e: (
                restyle(),
                _clear_combobox_selection(combobox),
            ),
            add="+",
        )
        combobox.bind(
            "<FocusOut>",
            lambda _e: combobox.after_idle(
                lambda: _clear_combobox_selection(combobox)
            ),
            add="+",
        )
    except (tk.TclError, AttributeError, TypeError):
        pass

    restyle()
    return combobox


def configure_styles(root: object, family: str | None = None) -> ttk.Style:
    """Configure the ttk styles used throughout the application.

    ``family`` may be supplied by ``MainWindow`` after its one-time font
    resolution. This avoids registering/querying the bundled fonts twice
    during startup.
    """
    if family is None:
        family = resolve_font_family(root)
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    # -----------------------------------------------------------------------
    # Text fields
    # -----------------------------------------------------------------------
    style.configure(
        "AG.TEntry",
        fieldbackground=FIELD_BG,
        background=FIELD_BG,
        foreground=FIELD_FG,
        insertcolor=TEXT_COLOR,
        selectbackground=FIELD_BG,
        selectforeground=FIELD_FG,
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        font=(family, 11),
        padding=7,
        borderwidth=0,
        relief="flat",
    )

    style.map(
        "AG.TEntry",
        fieldbackground=[
            ("focus", FIELD_FOCUS_BG),
            ("disabled", "#102A33"),
        ],
        foreground=[
            ("disabled", "#66818A"),
        ],
        bordercolor=[
            ("focus", FIELD_FOCUS),
            ("disabled", "#153A45"),
        ],
        lightcolor=[
            ("focus", FIELD_FOCUS),
            ("disabled", "#153A45"),
        ],
        darkcolor=[
            ("focus", FIELD_FOCUS),
            ("disabled", "#153A45"),
        ],
    )

    # -----------------------------------------------------------------------
    # Combobox popup frame
    # -----------------------------------------------------------------------
    # ttk creates the popup with this style name internally.  Configuring it
    # here avoids the default light/white frame around the Listbox.
    style.configure(
        "ComboboxPopdownFrame",
        background=FIELD_BG,
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        relief="solid",
        borderwidth=1,
    )

    # -----------------------------------------------------------------------
    # Comboboxes
    # -----------------------------------------------------------------------
    style.configure(
        "AG.TCombobox",
        fieldbackground=FIELD_BG,
        background=FIELD_BG,
        foreground=FIELD_FG,
        arrowcolor=TEXT_COLOR,
        insertcolor=TEXT_COLOR,
        selectbackground=FIELD_BG,
        selectforeground=FIELD_FG,
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        font=(family, 10),
        padding=6,
        borderwidth=1,
        relief="flat",
    )

    style.map(
        "AG.TCombobox",
        # Keep the complete Combobox surface dark in every interaction state.
        # On some Windows/Tk builds the clam theme otherwise paints the
        # arrow-side area white while the Combobox has focus.
        background=[
            ("disabled", FIELD_BG),
            ("readonly", FIELD_BG),
            ("focus", FIELD_BG),
            ("active", FIELD_BG),
            ("pressed", FIELD_BG),
            ("!disabled", FIELD_BG),
        ],
        fieldbackground=[
            ("readonly", FIELD_BG),
            ("focus", FIELD_BG),
            ("active", FIELD_BG),
            ("pressed", FIELD_BG),
        ],
        foreground=[
            ("readonly", FIELD_FG),
            ("focus", FIELD_FG),
        ],
        bordercolor=[
            ("focus", FIELD_FOCUS),
        ],
        lightcolor=[
            ("focus", FIELD_FOCUS),
        ],
        darkcolor=[
            ("focus", FIELD_FOCUS),
        ],
        arrowcolor=[
            ("disabled", TEXT_COLOR),
            ("readonly", TEXT_COLOR),
            ("focus", TEXT_COLOR),
            ("active", TEXT_COLOR),
            ("pressed", TEXT_COLOR),
            ("!disabled", TEXT_COLOR),
        ],
    )

    # The image element is installed after the style has been configured so
    # the arrow is independent of Tk/Windows' theme-specific arrow coloring.
    _install_combobox_arrow(style, root)

    # -----------------------------------------------------------------------
    # Progress
    # -----------------------------------------------------------------------
    style.configure(
        "AG.Horizontal.TProgressbar",
        troughcolor=MEDIA_BG,
        background=ACCENT_COLOR,
        bordercolor=MEDIA_BG,
        lightcolor=ACCENT_COLOR,
        darkcolor=ACCENT_COLOR,
        thickness=17,
    )

    # -----------------------------------------------------------------------
    # Secondary text
    # -----------------------------------------------------------------------
    style.configure(
        "AG.Secondary.TLabel",
        background=BG_COLOR,
        foreground=SECONDARY_TEXT_COLOR,
        font=(family, 10),
    )

    return style
