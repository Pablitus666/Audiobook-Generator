"""Reusable visual widgets for Audiobook Generator."""

import ctypes
import tkinter as tk
from ctypes import wintypes
from pathlib import Path
from tkinter import ttk, font as tkfont


def shorten_path(path: str, max_length: int = 72) -> str:
    """Shorten a long filesystem path for display without changing the real path.

    The beginning and the final portion are preserved so the user can still
    recognize the drive/location and the actual output file or folder.
    """
    value = str(path)
    if len(value) <= max_length:
        return value

    if max_length < 20:
        return value[: max(1, max_length - 3)] + "..."

    marker_length = 5  # "\\...\\"
    prefix_length = max(24, (max_length - marker_length) // 2)
    suffix_length = max_length - marker_length - prefix_length

    prefix = value[:prefix_length].rstrip("\\/")
    suffix = value[-suffix_length:].lstrip("\\/")

    return f"{prefix}\\...\\{suffix}"

from PIL import Image, ImageDraw, ImageTk

from .styles import ACCENT_COLOR, BG_COLOR, FIELD_BG, FONT_FALLBACK_FAMILY, FONT_FAMILY, SECONDARY_TEXT_COLOR, TEXT_COLOR, WIDGET_DARK, FIELD_BORDER, MEDIA_BG


GUI_ICON_FILENAME = "loguito.ico"


def configure_native_window_icons(
    window: tk.Misc,
    images_dir: Path,
    *,
    icon_filename: str = GUI_ICON_FILENAME,
) -> None:
    """Apply the GUI icon to every native icon slot of a Tk window.

    ``icon.ico`` is intentionally NOT used by the running GUI.  It is the
    PyInstaller executable icon declared in ``AudiobookGenerator.spec``.
    The running application's main window, taskbar icon, Alt+Tab icon and
    secondary dialogs all use ``loguito.ico``.

    The same ICO is loaded at both the small and large Win32 sizes so Windows
    can select the appropriate embedded image for each surface.  The native
    icon handles are retained on the window for its lifetime.
    """
    icon_path = Path(images_dir) / icon_filename

    if not icon_path.is_file():
        return

    # Tk fallback for non-Windows platforms and environments without Win32.
    if not hasattr(ctypes, "windll"):
        try:
            window.iconbitmap(default=str(icon_path))
            window.iconbitmap(str(icon_path))
        except (tk.TclError, OSError, ValueError):
            pass
        return

    try:
        hwnd = window.winfo_id()
        if not hwnd:
            raise OSError("Tk window handle is not available")

        user32 = ctypes.windll.user32

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x00000010
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1
        SM_CXICON = 11
        SM_CYICON = 12
        SM_CXSMICON = 49
        SM_CYSMICON = 50

        HWND = wintypes.HWND
        UINT = wintypes.UINT
        INT = wintypes.INT
        LPARAM = wintypes.LPARAM
        WPARAM = wintypes.WPARAM
        LRESULT = wintypes.LRESULT

        user32.LoadImageW.argtypes = [
            HWND, wintypes.LPCWSTR, UINT, INT, INT, UINT
        ]
        user32.LoadImageW.restype = ctypes.c_void_p
        user32.SendMessageW.argtypes = [
            HWND, UINT, WPARAM, LPARAM
        ]
        user32.SendMessageW.restype = LRESULT

        small_width = int(user32.GetSystemMetrics(SM_CXSMICON))
        small_height = int(user32.GetSystemMetrics(SM_CYSMICON))
        big_width = int(user32.GetSystemMetrics(SM_CXICON))
        big_height = int(user32.GetSystemMetrics(SM_CYICON))

        try:
            user32.GetDpiForWindow.argtypes = [HWND]
            user32.GetDpiForWindow.restype = UINT
            dpi = int(user32.GetDpiForWindow(hwnd))
            get_metrics_for_dpi = getattr(
                user32, "GetSystemMetricsForDpi", None
            )
            if dpi and get_metrics_for_dpi is not None:
                get_metrics_for_dpi.argtypes = [INT, UINT]
                get_metrics_for_dpi.restype = INT
                small_width = int(get_metrics_for_dpi(SM_CXSMICON, dpi))
                small_height = int(get_metrics_for_dpi(SM_CYSMICON, dpi))
                big_width = int(get_metrics_for_dpi(SM_CXICON, dpi))
                big_height = int(get_metrics_for_dpi(SM_CYICON, dpi))
        except (AttributeError, OSError, TypeError, ValueError):
            pass

        h_small = user32.LoadImageW(
            None, str(icon_path), IMAGE_ICON, small_width, small_height,
            LR_LOADFROMFILE,
        )
        h_big = user32.LoadImageW(
            None, str(icon_path), IMAGE_ICON, big_width, big_height,
            LR_LOADFROMFILE,
        )

        if not h_small or not h_big:
            raise OSError("Windows could not load the GUI ICO resources")

        window._native_window_icon = h_small
        window._native_large_icon = h_big

        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_big)

    except (AttributeError, OSError, TypeError, ValueError, tk.TclError):
        try:
            window.iconbitmap(default=str(icon_path))
            window.iconbitmap(str(icon_path))
        except (tk.TclError, OSError, ValueError):
            pass


def _font_family(widget) -> str:
    return getattr(widget.winfo_toplevel(), "font_family", FONT_FAMILY)


class AssetButton(tk.Button):
    """Graphical button based on the project's official button asset."""

    def __init__(self, master, image_manager, text, command=None, width=180, height=52, asset_filename="boton.png", **kwargs):
        # Resolve the font from the already-initialized parent.  ``self`` is
        # not a Tk widget until ``super().__init__`` has completed, so calling
        # ``self.winfo_toplevel()`` here would raise ``AttributeError: ... tk``.
        family = _font_family(master)
        self._command = command
        self._enabled = True
        self._image_manager = image_manager
        self._image = image_manager.load(asset_filename, width, height, enhance=True)
        super().__init__(
            master,
            image=self._image,
            text=text,
            compound="center",
            fg="white",
            bg=BG_COLOR,
            activebackground=BG_COLOR,
            activeforeground="#fcbf49",
            font=(family, 12, "bold"),
            cursor="hand2",
            bd=0,
            highlightthickness=0,
            highlightcolor=BG_COLOR,
            highlightbackground=BG_COLOR,
            relief="flat",
            command=self._on_click,
            **kwargs,
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _event):
        if self._enabled:
            self.configure(fg="#fcbf49")

    def _on_leave(self, _event):
        if self._enabled:
            self.configure(fg="white")

    def _on_press(self, _event):
        if self._enabled:
            self.configure(fg="#fcbf49")

    def _on_release(self, _event):
        if self._enabled:
            self.configure(fg="#fcbf49" if self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery()) is self else "white")

    def _on_click(self):
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable the command without changing the button appearance.

        The GUI already communicates generation progress through the status
        text and progress bar.  A disabled/greyed asset button would break the
        visual identity, so the button remains visually identical while its
        command is ignored until generation finishes.
        """
        self._enabled = enabled
        # Keep the established visual state unchanged while busy.
        self.configure(cursor="hand2", fg="white")


class StyledMessageDialog(tk.Toplevel):
    """Compact application-styled modal message dialog."""

    WIDTH = 450
    HEIGHT = 180

    @staticmethod
    def _fit_message_to_three_lines(message, font, max_width=304, max_lines=3):
        """Fit dialog text into at most three visual lines."""
        text = str(message).strip()
        if not text:
            return ""

        def split_long_word(word):
            chunks = []
            remaining = word
            while remaining:
                chunk = ""
                for char in remaining:
                    candidate = chunk + char
                    if font.measure(candidate) <= max_width:
                        chunk = candidate
                    else:
                        break
                if not chunk:
                    chunk = remaining[0]
                chunks.append(chunk)
                remaining = remaining[len(chunk):]
            return chunks

        lines = []
        current = ""

        for word in text.split():
            if font.measure(word) > max_width:
                if current:
                    lines.append(current)
                    current = ""

                chunks = split_long_word(word)
                for chunk in chunks:
                    if len(lines) >= max_lines:
                        break
                    lines.append(chunk)
                if len(lines) >= max_lines:
                    break
                continue

            candidate = word if not current else f"{current} {word}"
            if font.measure(candidate) <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
            current = word

            if len(lines) >= max_lines:
                break

        if len(lines) < max_lines and current:
            lines.append(current)

        if len(lines) < max_lines:
            return "\n".join(lines)

        # If content still remains beyond the third line, make the third line
        # visibly indicate truncation without exceeding the text area.
        consumed = " ".join(lines)
        if len(consumed) < len(text):
            last = lines[-1].rstrip()
            while last and font.measure(last + "…") > max_width:
                last = last[:-1]
            lines[-1] = (last + "…") if last else "…"

        return "\n".join(lines[:max_lines])

    def __init__(
        self,
        parent,
        title: str,
        message: str,
        kind: str = "info",
        action_label: str | None = None,
        action_command=None,
    ):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.title(title)
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(parent)

        images_dir = getattr(getattr(parent, "images", None), "images_dir", None)
        if images_dir is not None:
            configure_native_window_icons(self, images_dir)

        family = _font_family(self)
        emoji = {"error": "❌", "info": "ℹ️"}.get(kind, "ℹ️")

        self._message_icon = None
        message_icons = {
            "warning": "alert_warning.png",
            "success": "success.png",
            "error": "error.png",
            "info": "info.png",
        }
        icon_filename = message_icons.get(kind)
        if icon_filename and getattr(parent, "images", None) is not None:
            try:
                self._message_icon = parent.images.load(
                    icon_filename, 80, 80, enhance=False
                )
            except (OSError, ValueError, tk.TclError):
                self._message_icon = None

        outer = tk.Frame(self, bg=BG_COLOR, bd=0, highlightthickness=0)
        outer.place(x=18, y=5, width=self.WIDTH - 36, height=self.HEIGHT - 10)

        if self._message_icon is not None:
            icon_label = tk.Label(
                outer,
                image=self._message_icon,
                bg=BG_COLOR,
                bd=0,
                highlightthickness=0,
            )
            icon_label.place(x=0, y=25, width=80, height=80)
        else:
            icon_label = tk.Label(
                outer,
                text=emoji,
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI Emoji", 26),
                bd=0,
                highlightthickness=0,
            )
            icon_label.place(x=0, y=25, width=80, height=50)

        message_font = tkfont.Font(family=family, size=12)
        display_message = self._fit_message_to_three_lines(
            message,
            message_font,
            max_width=304,
            max_lines=3,
        )

        message_label = tk.Label(
            outer,
            text=display_message,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=message_font,
            justify="center",
            anchor="center",
            wraplength=304,
            bd=0,
            highlightthickness=0,
        )
        message_label.place(x=92, y=10, width=304, height=90)

        image_manager = getattr(parent, "images", None)
        ok_text = getattr(
            getattr(parent, "i18n", None), "t", lambda key: "OK"
        )("button.ok")
        has_action = action_command is not None and bool(action_label)

        if image_manager is not None:
            if has_action:
                action = AssetButton(
                    outer,
                    image_manager,
                    action_label,
                    command=action_command,
                    width=130,
                    height=48,
                    asset_filename="boton1.png",
                    takefocus=False,
                )
                action.place(x=113, y=112, width=140, height=48)

            ok = AssetButton(
                outer,
                image_manager,
                ok_text,
                command=self.destroy,
                width=130,
                height=48,
                takefocus=False,
            )
        else:
            if has_action:
                action = tk.Button(
                    outer,
                    text=action_label,
                    command=action_command,
                    bg="#087EA4",
                    fg=TEXT_COLOR,
                    font=(family, 10, "bold"),
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    takefocus=False,
                )
                action.place(x=113, y=112, width=140, height=48)

            ok = tk.Button(
                outer,
                text=ok_text,
                command=self.destroy,
                bg="#087EA4",
                fg=TEXT_COLOR,
                font=(family, 10, "bold"),
                relief="flat",
                bd=0,
                highlightthickness=0,
                takefocus=False,
            )

        ok.place(x=263, y=112, width=140, height=48)

        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(self.WIDTH, self.HEIGHT)
        self.maxsize(self.WIDTH, self.HEIGHT)
        self.update_idletasks()
        self._center()
        self.grab_set()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.wait_window()

    def _center(self):
        """Center the dialog on the physical screen."""
        self.update_idletasks()
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            px = (screen_width - self.WIDTH) // 2
            py = (screen_height - self.HEIGHT) // 2
            self.geometry(
                f"{self.WIDTH}x{self.HEIGHT}"
                f"+{max(0, px)}+{max(0, py)}"
            )
        except tk.TclError:
            self.geometry(f"{self.WIDTH}x{self.HEIGHT}")


def show_message_dialog(
    parent,
    title: str,
    message: str,
    kind: str = "info",
    action_label: str | None = None,
    action_command=None,
) -> None:
    """Show a modal application-styled dialog with an optional action button."""
    StyledMessageDialog(
        parent,
        title,
        message,
        kind=kind,
        action_label=action_label,
        action_command=action_command,
    )


class SwitchToggle(tk.Frame):
    """High-resolution pill switch with a crisp, Windows-friendly finish."""

    WIDTH = 62
    HEIGHT = 32
    _SCALE = 8
    _ANIMATION_MS = 18
    _ANIMATION_STEPS = 7

    def __init__(self, master, text: str, variable: tk.BooleanVar):
        super().__init__(master, bg=BG_COLOR)
        self.variable = variable
        self._hover = False
        self._photo = None
        self._animation_job = None
        self._visual_position = 1.0 if bool(variable.get()) else 0.0

        self.canvas = tk.Label(
            self,
            bg=BG_COLOR,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(side="left")
        self.label = tk.Label(
            self,
            text=text,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=(_font_family(self), 10, "bold"),
            cursor="hand2",
        )
        self.label.pack(side="left", padx=(10, 0))

        for widget in (self, self.canvas, self.label):
            widget.bind("<Button-1>", self._toggle)
            widget.bind("<Enter>", self._enter)
            widget.bind("<Leave>", self._leave)
        self._refresh()

    def _toggle(self, _event=None):
        self.variable.set(not self.variable.get())
        self._animate_to(1.0 if self.variable.get() else 0.0)

    def _enter(self, _event=None):
        self._hover = True
        self._refresh()
        self.label.configure(fg=ACCENT_COLOR)

    def _leave(self, _event=None):
        self._hover = False
        self._refresh()
        self.label.configure(fg=TEXT_COLOR)

    def _animate_to(self, target: float) -> None:
        if self._animation_job is not None:
            try:
                self.after_cancel(self._animation_job)
            except Exception:
                pass
            self._animation_job = None

        start = self._visual_position
        delta = target - start
        if abs(delta) < 0.01:
            self._visual_position = target
            self._refresh()
            return

        step = 0

        def advance() -> None:
            nonlocal step
            step += 1
            progress = min(1.0, step / self._ANIMATION_STEPS)
            # Smoothstep easing: gentle start and finish.
            eased = progress * progress * (3.0 - 2.0 * progress)
            self._visual_position = start + delta * eased
            self._refresh()
            if progress < 1.0:
                self._animation_job = self.after(self._ANIMATION_MS, advance)
            else:
                self._animation_job = None

        advance()

    def _refresh(self):
        active = bool(self.variable.get())
        scale = self._SCALE
        width = self.WIDTH * scale
        height = self.HEIGHT * scale
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        radius = height // 2
        if active:
            track = ACCENT_COLOR
            outline = ACCENT_COLOR
        else:
            track = "#16465A"
            outline = SECONDARY_TEXT_COLOR
        if self._hover:
            outline = TEXT_COLOR if not active else ACCENT_COLOR

        draw.rounded_rectangle(
            (scale, scale, width - scale, height - scale),
            radius=radius - scale,
            fill=track,
            outline=outline,
            width=max(2, scale // 2),
        )

        # Keep the active track clean: no horizontal highlight line is drawn.

        knob_radius = int(height * 0.34)
        center_y = height // 2
        left = int(height * 0.50)
        right = width - int(height * 0.50)
        center_x = int(left + (right - left) * self._visual_position)

        # Soft shadow, rendered separately so the knob remains crisp after downsampling.
        shadow_offset = max(2, scale // 2)
        draw.ellipse(
            (center_x - knob_radius + shadow_offset, center_y - knob_radius + shadow_offset,
             center_x + knob_radius + shadow_offset, center_y + knob_radius + shadow_offset),
            fill=(0, 0, 0, 65),
        )
        draw.ellipse(
            (center_x - knob_radius, center_y - knob_radius,
             center_x + knob_radius, center_y + knob_radius),
            fill=(255, 255, 255, 255),
            outline=(235, 235, 235, 255),
            width=max(1, scale // 3),
        )

        image = image.resize((self.WIDTH, self.HEIGHT), Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(image, master=self)
        self.canvas.configure(image=self._photo)


class SectionHeader(tk.Frame):
    """Small section title with a restrained accent rule."""

    def __init__(self, master, title: str, subtitle: str | None = None):
        super().__init__(master, bg=BG_COLOR)
        bar = tk.Frame(self, bg=ACCENT_COLOR, width=4, height=24)
        bar.pack(side="left", padx=(0, 10))
        text_box = tk.Frame(self, bg=BG_COLOR)
        text_box.pack(side="left")
        tk.Label(
            text_box,
            text=title.upper(),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=(_font_family(self), 10, "bold"),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                text_box,
                text=subtitle,
                bg=BG_COLOR,
                fg=SECONDARY_TEXT_COLOR,
                font=(_font_family(self), 9),
            ).pack(anchor="w", pady=(1, 0))


class FieldFrame(tk.Frame):
    """Visually grouped field used for long paths."""

    def __init__(self, master, variable, button):
        super().__init__(master, bg=BG_COLOR)
        self.entry = ttk.Entry(self, textvariable=variable, style="AG.TEntry")
        self.entry.pack(side="left", fill="x", expand=True, ipady=2)
        button.pack(side="left", padx=(10, 0))


class StatusBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.variable = tk.StringVar(value="Preparado")
        ttk.Label(self, textvariable=self.variable, style="AG.Secondary.TLabel").pack(anchor="w")

    def set(self, text: str) -> None:
        self.variable.set(text)
