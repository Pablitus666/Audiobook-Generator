"""About dialog for Audiobook Generator."""

import tkinter as tk
from tkinter import Toplevel

from .styles import ACCENT_COLOR, BG_COLOR, FONT_FAMILY, TEXT_COLOR
from .widgets import configure_native_window_icons


class AboutWindow(Toplevel):
    """Information window opened from the application logo."""

    # Keep the established About-window proportions used before the HiDPI
    # image changes.  The dimensions are logical Tk units.
    WIDTH = 370
    HEIGHT = 230

    def __init__(self, parent, image_manager):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.image_manager = image_manager
        self.i18n = parent.i18n
        self.title(self.i18n.t("window.about.title"))
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.robot_img = None
        self.button_img = None

        self._load_assets()

        configure_native_window_icons(
            self,
            self.image_manager.images_dir,
        )

        self._create_widgets()
        self._center_popup()
        self.transient(parent)
        self.grab_set()
        self.deiconify()
        self.lift()
        self.focus_force()

    def _load_assets(self) -> None:
        # Render artwork through the shared DPI-aware ImageManager so the
        # images remain sharp on high-density displays.
        self.robot_img = self.image_manager.load(
            "robot.png", 135, 155, enhance=True
        )
        self.button_img = self.image_manager.load(
            "boton.png", 150, 55, enhance=True
        )

    def _create_widgets(self) -> None:
        frame = tk.Frame(
            self,
            bg=BG_COLOR,
            bd=0,
            highlightthickness=0,
        )
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Two balanced columns.  Keep the author text at the same visual
        # scale as the established About window; the surrounding Tk scaling
        # handles the actual display DPI.
        frame.grid_columnconfigure(0, minsize=155, weight=0)
        frame.grid_columnconfigure(1, minsize=190, weight=0)
        frame.grid_rowconfigure(0, minsize=115, weight=0)
        frame.grid_rowconfigure(1, minsize=70, weight=0)

        robot_label = tk.Label(
            frame,
            image=self.robot_img,
            bg=BG_COLOR,
            bd=0,
            highlightthickness=0,
        )
        robot_label.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(0, 2),
            pady=0,
            sticky="nsew",
        )

        font_family = getattr(self.parent, "font_family", FONT_FAMILY)

        author_label = tk.Label(
            frame,
            text=self.i18n.t("info.developed_by"),
            justify="center",
            anchor="center",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=(font_family, 16, "bold"),
            bd=0,
            highlightthickness=0,
        )
        author_label.grid(
            row=0,
            column=1,
            padx=(0, 2),
            pady=(14, 0),
            sticky="nsew",
        )

        button_holder = tk.Frame(
            frame,
            bg=BG_COLOR,
            bd=0,
            highlightthickness=0,
        )
        button_holder.grid(
            row=1,
            column=1,
            padx=(0, 2),
            pady=(8, 0),
            sticky="nsew",
        )

        close_button = tk.Button(
            button_holder,
            image=self.button_img,
            text=self.i18n.t("button.close"),
            compound="center",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            activebackground=BG_COLOR,
            activeforeground=ACCENT_COLOR,
            font=(font_family, 10, "bold"),
            bd=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            command=self.destroy,
        )
        close_button.place(relx=0.5, rely=0.5, anchor="center")

        def on_enter(_event):
            close_button.configure(fg=ACCENT_COLOR)

        def on_leave(_event):
            close_button.configure(fg=TEXT_COLOR)
            close_button.place_configure(rely=0.5, y=0)

        def on_press(_event):
            close_button.configure(fg=ACCENT_COLOR)
            close_button.place_configure(rely=0.5, y=2)

        def on_release(_event):
            close_button.place_configure(rely=0.5, y=0)
            inside = (
                close_button.winfo_containing(
                    close_button.winfo_pointerx(),
                    close_button.winfo_pointery(),
                )
                is close_button
            )
            close_button.configure(fg=ACCENT_COLOR if inside else TEXT_COLOR)

        close_button.bind("<Enter>", on_enter)
        close_button.bind("<Leave>", on_leave)
        close_button.bind("<ButtonPress-1>", on_press)
        close_button.bind("<ButtonRelease-1>", on_release)

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _center_popup(self) -> None:
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.WIDTH) // 2
        y = (screen_height - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
