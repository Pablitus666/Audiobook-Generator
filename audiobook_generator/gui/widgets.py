"""Reusable visual widgets for Audiobook Generator."""

import tkinter as tk
from tkinter import ttk


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


def _font_family(widget) -> str:
    return getattr(widget.winfo_toplevel(), "font_family", FONT_FAMILY)


class AssetButton(tk.Button):
    """Graphical button based on the project's official button asset."""

    def __init__(self, master, image_manager, text, command=None, width=180, height=52, **kwargs):
        # Resolve the font from the already-initialized parent.  ``self`` is
        # not a Tk widget until ``super().__init__`` has completed, so calling
        # ``self.winfo_toplevel()`` here would raise ``AttributeError: ... tk``.
        family = _font_family(master)
        self._command = command
        self._enabled = True
        self._image_manager = image_manager
        self._image = image_manager.load("boton.png", width, height, enhance=True)
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
    HEIGHT = 160

    def __init__(self, parent, title: str, message: str, kind: str = "info"):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.title(title)
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.transient(parent)

        icon_path = getattr(getattr(parent, "images", None), "images_dir", None)
        if icon_path is not None:
            icon_file = icon_path / "icon.ico"
            if icon_file.is_file():
                try:
                    self.iconbitmap(default=str(icon_file))
                except (tk.TclError, OSError, ValueError):
                    pass

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

        # IMPORTANT: the dialog layout is deliberately fixed.  Nothing inside
        # it is allowed to participate in geometry negotiation.  This prevents
        # a long path from moving the icon, text, or OK button.
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
            # This deliberately corresponds to the established
            # pady=(25, 0) visual position of the warning/success images.
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

        # The message area is explicitly bounded to the space to the right of
        # the icon.  In particular, do not use relwidth=1.0 here: that would
        # make the label extend past the right edge of the dialog.
        message_label = tk.Label(
            outer,
            text=message,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=(family, 12),
            justify="center",
            anchor="center",
            wraplength=300,
            bd=0,
            highlightthickness=0,
        )
        message_label.place(x=92, y=18, width=304, height=72)

        image_manager = getattr(parent, "images", None)
        if image_manager is not None:
            ok = AssetButton(
                outer,
                image_manager,
                getattr(getattr(parent, "i18n", None), "t", lambda key: "OK")("button.ok"),
                command=self.destroy,
                width=130,
                height=48,
                takefocus=False,
            )
        else:
            ok = tk.Button(
                outer,
                text=getattr(getattr(parent, "i18n", None), "t", lambda key: "OK")("button.ok"),
                command=self.destroy,
                bg="#087EA4",
                fg=TEXT_COLOR,
                font=(family, 10, "bold"),
                relief="flat",
                bd=0,
                highlightthickness=0,
                takefocus=False,
            )

        # Fixed position: the button cannot be pushed down by message text.
        ok.place(x=263, y=95, width=140, height=48)

        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Fixed native client size.  The content above is positioned inside
        # this rectangle and therefore cannot enlarge or rearrange the window.
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
        self.update_idletasks()
        parent = self.parent
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() - self.WIDTH) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - self.HEIGHT) // 2
        except tk.TclError:
            px = (self.winfo_screenwidth() - self.WIDTH) // 2
            py = (self.winfo_screenheight() - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{max(0, px)}+{max(0, py)}")

def show_message_dialog(parent, title: str, message: str, kind: str = "info") -> None:
    """Show a modal application-styled information/warning/error dialog."""
    StyledMessageDialog(parent, title, message, kind=kind)


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
