"""Main graphical interface for Audiobook Generator."""

import asyncio
import queue
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:  # pragma: no cover - fallback keeps non-GUI test imports usable
    DND_FILES = None

    class _TkinterDnDFallback:
        Tk = tk.Tk

    TkinterDnD = _TkinterDnDFallback()

from .about_window import AboutWindow
from ..core.config import AudiobookConfig, OcrConfig, OutputConfig, ProcessingConfig, TTSConfig
from ..core.dpi import enable_dpi_awareness, get_tkinter_scalefactor
from ..core.errors import AudiobookError
from ..core.localization import Localization
from ..core.pipeline import AudiobookPipeline
from ..core.voices import resolve_voice
from ..readers.factory import ReaderFactory
from .image_manager import ImageManager
from .styles import ACCENT_COLOR, BG_COLOR, FIELD_BG, FIELD_BORDER, FONT_FAMILY, MEDIA_BG, SECONDARY_TEXT_COLOR, TEXT_COLOR, configure_styles, prepare_combobox, resolve_font_family
from .widgets import AssetButton, SectionHeader, StatusBar, SwitchToggle, shorten_path, show_message_dialog


class MainWindow(TkinterDnD.Tk):
    """Primary Audiobook Generator window."""

    WINDOW_WIDTH = 860
    WINDOW_HEIGHT = 600
    APP_USER_MODEL_ID = "Pablitus.AudiobookGenerator"
    ICON_FILENAME = "icon.ico"

    def __init__(self) -> None:
        enable_dpi_awareness()
        self._set_windows_app_user_model_id()
        self.i18n = Localization()
        super().__init__()
        # Keep the root hidden while the window, icon, images and geometry are
        # being prepared. This prevents Tk from briefly showing a small
        # unstyled/black window during startup.
        self.withdraw()
        self.title(self.i18n.t("app.title"))
        self.scale_factor = get_tkinter_scalefactor(self)
        self.font_family = resolve_font_family(self)
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.option_add("*Font", (self.font_family, 10))

        configure_styles(self)
        self.images = ImageManager(self, scale=self.scale_factor)
        self._configure_window_icon()

        self.output_dir = tk.StringVar(value="")
        self.input_path = tk.StringVar()
        self.voice = tk.StringVar(value="Sofía")
        self.speed = tk.StringVar(value="+0%")
        self.volume = tk.StringVar(value="+0%")
        self.pitch = tk.StringVar(value="+0Hz")
        self.max_characters = tk.StringVar(value="1500")
        self.keep_chapters = tk.BooleanVar(value=True)
        self.progress = tk.DoubleVar(value=0)
        self._generation_queue: queue.Queue[tuple] = queue.Queue()
        self._generation_running = False
        self._generation_thread: threading.Thread | None = None

        self._build_ui()
        self.bind_all("<Return>", self._on_global_return)
        self._center_window()
        self.deiconify()
        self.lift()
        self.focus_force()

    @classmethod
    def _set_windows_app_user_model_id(cls) -> None:
        try:
            import ctypes
            if hasattr(ctypes, "windll"):
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(cls.APP_USER_MODEL_ID)
        except Exception:
            pass

    def _configure_window_icon(self) -> None:
        """Configure the native Tk/Windows application icon.

        Keep icon handling deliberately simple: Tk receives the real multi-size
        ICO, while a 256px PNG is kept as a PhotoImage fallback for Tk surfaces
        that do not use the ICO directly.  The icon is assigned while the root
        is still withdrawn, before the first ``deiconify()``.
        """
        icon_dir = self.images.images_dir
        ico_path = icon_dir / self.ICON_FILENAME
        png_path = icon_dir / "icon_256.png"

        if ico_path.is_file():
            try:
                # On Windows this is the native path for the title-bar icon.
                # Do not resize/re-encode the ICO in Python.
                self.iconbitmap(default=str(ico_path))
                self.iconbitmap(str(ico_path))
            except (tk.TclError, OSError, ValueError):
                pass

        if png_path.is_file():
            try:
                self._window_icon_photo = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._window_icon_photo)
            except (tk.TclError, OSError, ValueError):
                pass

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=BG_COLOR)
        outer.pack(fill="both", expand=True, padx=22, pady=14)

        # Header ---------------------------------------------------------
        header = tk.Frame(outer, bg=BG_COLOR, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        group = tk.Frame(header, bg=BG_COLOR)
        group.place(relx=0.5, rely=0.5, anchor="center")
        logo = self.images.load("logo.png", 68, 68, enhance=True)
        logo_button = tk.Label(
            group,
            image=logo,
            bg=BG_COLOR,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        logo_button.pack(side="left", padx=(0, 13))
        logo_button.bind("<Button-1>", lambda _event: self._show_about_window())

        title = self.images.load("titulo.png", 520, 58, enhance=True)
        tk.Label(group, image=title, bg=BG_COLOR, bd=0, highlightthickness=0).pack(side="left")

        tk.Frame(outer, bg="#A1D6E2", height=1).pack(fill="x", pady=(3, 8))

        # Document -------------------------------------------------------
        SectionHeader(outer, self.i18n.t("section.document")).pack(anchor="w")
        source_row = tk.Frame(outer, bg=BG_COLOR)
        source_row.pack(fill="x", pady=(7, 8))
        source_shell = tk.Frame(source_row, bg=FIELD_BORDER, bd=0, highlightthickness=0)
        source_shell.pack(side="left", fill="x", expand=True, ipady=1)
        source_entry = tk.Entry(
            source_shell,
            textvariable=self.input_path,
            state="readonly",
            readonlybackground=FIELD_BG,
            bg=FIELD_BG,
            fg=TEXT_COLOR,
            disabledforeground=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=(self.font_family, 11),
            takefocus=1,
        )
        source_entry.pack(fill="both", expand=True, padx=1, pady=1, ipady=6)
        self._bind_path_clear_keys(source_entry, self.input_path, reset_progress=True)
        self._enable_input_drag_and_drop(source_entry)
        AssetButton(source_row, self.images, self.i18n.t("button.browse"), self._browse_document, 126, 44).pack(side="left", padx=(12, 0))

        # Configuration card --------------------------------------------
        config_card = tk.Frame(outer, bg="#063A50", highlightbackground="#0B5A72", highlightthickness=1)
        config_card.pack(fill="x", pady=(0, 14))
        config_inner = tk.Frame(config_card, bg="#063A50")
        config_inner.pack(fill="x", padx=18, pady=10)
        tk.Label(
            config_inner,
            text=self.i18n.t("section.narration"),
            bg="#063A50",
            fg=TEXT_COLOR,
            font=(self.font_family, 10, "bold"),
        ).pack(anchor="w")
        tk.Frame(config_inner, bg=ACCENT_COLOR, height=2).pack(fill="x", pady=(6, 12))

        controls = tk.Frame(config_inner, bg="#063A50")
        controls.pack(fill="x")
        for i in range(5):
            controls.grid_columnconfigure(i, weight=1, uniform="config")

        groups = [
            (self.i18n.t("label.voice"), self.voice, ["Sofía", "Elvira", "Marcelo", "Álvaro"]),
            (self.i18n.t("label.speed"), self.speed, ["-20%", "-10%", "+0%", "+10%", "+20%"]),
            (self.i18n.t("label.volume"), self.volume, ["-20%", "-10%", "+0%", "+10%", "+20%"]),
            (self.i18n.t("label.pitch"), self.pitch, ["-20Hz", "-10Hz", "+0Hz", "+10Hz", "+20Hz"]),
            (self.i18n.t("label.max_characters"), self.max_characters, None),
        ]
        for column, (label, variable, values) in enumerate(groups):
            cell = tk.Frame(controls, bg="#063A50")
            cell.grid(row=0, column=column, sticky="ew", padx=6)
            tk.Label(cell, text=label, bg="#063A50", fg=SECONDARY_TEXT_COLOR, font=(self.font_family, 9, "bold")).pack(anchor="center", pady=(0, 5))
            if values is None:
                entry_shell = tk.Frame(cell, bg=FIELD_BORDER, bd=0, highlightthickness=0)
                entry_shell.pack(fill="x", ipady=1)
                ttk.Entry(entry_shell, textvariable=variable, style="AG.TEntry", justify="center", width=12).pack(fill="both", expand=True, padx=1, pady=1, ipady=2)
            else:
                prepare_combobox(ttk.Combobox(cell, textvariable=variable, values=values, state="readonly", style="AG.TCombobox", justify="center")).pack(fill="x", ipady=1)

        # Output ---------------------------------------------------------
        SectionHeader(outer, self.i18n.t("section.output")).pack(anchor="w")
        output_row = tk.Frame(outer, bg=BG_COLOR)
        output_row.pack(fill="x", pady=(7, 4))
        output_shell = tk.Frame(output_row, bg=FIELD_BORDER, bd=0, highlightthickness=0)
        output_shell.pack(side="left", fill="x", expand=True, ipady=1)
        output_entry = tk.Entry(
            output_shell,
            textvariable=self.output_dir,
            state="readonly",
            readonlybackground=FIELD_BG,
            bg=FIELD_BG,
            fg=TEXT_COLOR,
            disabledforeground=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=(self.font_family, 11),
            takefocus=1,
        )
        output_entry.pack(fill="both", expand=True, padx=1, pady=1, ipady=6)
        self._bind_path_clear_keys(output_entry, self.output_dir)
        AssetButton(output_row, self.images, self.i18n.t("button.browse"), self._browse_output, 126, 44).pack(side="left", padx=(12, 0))

        # Options --------------------------------------------------------
        options = tk.Frame(outer, bg=BG_COLOR)
        options.pack(fill="x", pady=(1, 5))
        self.keep_toggle = SwitchToggle(options, self.i18n.t("label.keep_chapters"), self.keep_chapters)
        self.keep_toggle.pack(anchor="center")

        # Primary action -------------------------------------------------
        action = tk.Frame(outer, bg=BG_COLOR)
        action.pack(pady=(1, 5))
        self.generate_button = AssetButton(action, self.images, self.i18n.t("button.generate"), self._start_generation, 202, 56)
        self.generate_button.pack()

        # Progress -------------------------------------------------------
        progress_section = tk.Frame(outer, bg=BG_COLOR)
        progress_section.pack(fill="x")
        progress_header = tk.Frame(progress_section, bg=BG_COLOR)
        progress_header.pack(fill="x", pady=(0, 5))
        tk.Label(progress_header, text=self.i18n.t("label.progress"), bg=BG_COLOR, fg=TEXT_COLOR, font=(self.font_family, 9, "bold")).pack(side="left")
        self.progress_value = tk.Label(progress_header, text="0%", bg=BG_COLOR, fg=SECONDARY_TEXT_COLOR, font=(self.font_family, 9))
        self.progress_value.pack(side="right")
        progress_track = tk.Frame(
            progress_section,
            bg=MEDIA_BG,
            height=17,
            bd=0,
            highlightthickness=1,
            highlightbackground="#14566A",
        )
        progress_track.pack(fill="x")
        progress_track.pack_propagate(False)
        ttk.Progressbar(
            progress_track,
            variable=self.progress,
            maximum=100,
            style="AG.Horizontal.TProgressbar",
        ).pack(fill="both", expand=True)
        self.status = StatusBar(progress_section)
        self.status.pack(fill="x", pady=(6, 0))
        self.status.set(self.i18n.t("status.ready"))

    def _bind_path_clear_keys(
        self, entry: tk.Entry, variable: tk.StringVar, reset_progress: bool = False
    ) -> None:
        """Allow Backspace/Delete to clear a selected input or output path.

        The path fields remain readonly so users cannot accidentally edit a
        filesystem path character-by-character.  They can, however, focus the
        field and clear the complete value when they want to discard an
        incorrect selection and choose another path.
        """

        def clear_path(_event=None):
            variable.set("")
            if reset_progress and not self._generation_running:
                self.progress.set(0)
                self.progress_value.configure(text="0%")
                self.status.set(self.i18n.t("status.ready"))
            return "break"

        entry.bind("<BackSpace>", clear_path)
        entry.bind("<Delete>", clear_path)

    def _enable_input_drag_and_drop(self, entry: tk.Entry) -> None:
        """Register only the Input field as a Windows drag-and-drop target."""
        if DND_FILES is None or not hasattr(entry, "drop_target_register"):
            return
        try:
            entry.drop_target_register(DND_FILES)
            entry.dnd_bind("<<Drop>>", self._handle_input_drop)
        except (tk.TclError, AttributeError):
            # Drag-and-drop is optional at runtime; the Browse button remains
            # fully functional if TkDnD is unavailable.
            pass

    def _handle_input_drop(self, event) -> str:
        """Put the first dropped file path into the Input field."""
        try:
            paths = self.tk.splitlist(event.data)
            if not paths:
                return "break"
            # Accept only formats the application can actually read.
            # A drag operation containing several files is intentionally
            # reduced to the first valid supported document.
            for path in paths:
                if path and Path(path).suffix.lower() in ReaderFactory._READERS:
                    self._set_input_path(path)
                    break
        except (tk.TclError, AttributeError, TypeError):
            pass
        return "break"

    def _on_global_return(self, event=None):
        """Start generation when Enter is pressed in the main window.

        Dialogs keep their own Return binding; this handler only responds
        when the focused widget belongs to the main application window.
        """
        if event is None:
            return
        try:
            if event.widget.winfo_toplevel() is not self:
                return
            # Let buttons and comboboxes keep their native Enter behavior.
            # Enter acts as the Generate shortcut from the path fields and
            # the rest of the main window.
            if isinstance(event.widget, (tk.Button, ttk.Combobox)):
                return
        except tk.TclError:
            return
        self._start_generation()
        return "break"

    def _show_about_window(self) -> None:
        if getattr(self, "about_window", None) is None or not self.about_window.winfo_exists():
            self.about_window = AboutWindow(self, self.images)
        else:
            self.about_window.deiconify()
        self.about_window.lift()
        self.about_window.focus_force()

    def _browse_document(self):
        path = filedialog.askopenfilename(
            title=self.i18n.t("dialog.select_document.title"),
            filetypes=[
                (self.i18n.t("filetype.supported_documents"), "*.txt *.md *.markdown *.pdf *.docx *.epub *.rtf *.html *.htm *.xhtml *.odt"),
                (self.i18n.t("filetype.all_files"), "*.*"),
            ],
        )
        if path:
            self._set_input_path(path)

    def _set_input_path(self, path: str) -> None:
        self.input_path.set(path)
        if not self._generation_running:
            self.progress.set(0)
            self.progress_value.configure(text="0%")
            self.status.set(self.i18n.t("status.ready"))

    def _browse_output(self):
        path = filedialog.askdirectory(title=self.i18n.t("dialog.select_output.title"))
        if path:
            self.output_dir.set(path)

    def _start_generation(self) -> None:
        """Validate the GUI state and start the pipeline off the Tk thread."""
        if self._generation_running:
            return

        source_text = self.input_path.get().strip()
        if not source_text:
            show_message_dialog(
                self,
                self.i18n.t("dialog.warning.title"),
                self.i18n.t("dialog.warning.select_document"),
                kind="warning",
            )
            return

        source = Path(source_text).expanduser().resolve()
        if not source.is_file():
            show_message_dialog(
                self,
                self.i18n.t("dialog.error.title"),
                f"{self.i18n.t('dialog.error.invalid_document')}\n{shorten_path(source)}",
                kind="error",
            )
            return

        if source.suffix.lower() not in ReaderFactory._READERS:
            show_message_dialog(
                self,
                self.i18n.t("dialog.error.title"),
                f"{self.i18n.t('dialog.error.invalid_document')}\n{shorten_path(source)}",
                kind="error",
            )
            return

        try:
            max_characters = int(self.max_characters.get().strip())
        except (TypeError, ValueError):
            max_characters = 0

        if max_characters <= 0:
            show_message_dialog(
                self,
                self.i18n.t("dialog.error.title"),
                self.i18n.t("dialog.error.invalid_max_characters"),
                kind="error",
            )
            return

        output_text = self.output_dir.get().strip()
        output_dir = (
            Path(output_text).expanduser().resolve()
            if output_text
            else source.parent
        )
        if not output_text:
            self.output_dir.set(str(output_dir))

        try:
            voice = resolve_voice(self.voice.get()).voice
        except ValueError as exc:
            show_message_dialog(
                self,
                self.i18n.t("dialog.error.title"),
                str(exc),
                kind="error",
            )
            return

        config = AudiobookConfig(
            tts=TTSConfig(
                voice=voice,
                rate=self.speed.get(),
                volume=self.volume.get(),
                pitch=self.pitch.get(),
            ),
            output=OutputConfig(bitrate="192k"),
            processing=ProcessingConfig(
                max_characters=max_characters,
                temp_dir=output_dir / ".audiobook_generator_temp",
                keep_chapters=bool(self.keep_chapters.get()),
            ),
            ocr=OcrConfig(),
        )

        self._generation_running = True
        self.generate_button.set_enabled(False)
        self.progress.set(0)
        self.progress_value.configure(text="0%")
        self.status.set(self.i18n.t("status.loading"))

        self._generation_thread = threading.Thread(
            target=self._generation_worker,
            args=(source, output_dir, config),
            daemon=True,
        )
        self._generation_thread.start()
        self.after(100, self._poll_generation_queue)

    def _generation_worker(
        self,
        source: Path,
        output_dir: Path,
        config: AudiobookConfig,
    ) -> None:
        """Run document reading, TTS and FFmpeg without blocking Tk."""
        try:
            if source.suffix.lower() == ".pdf":
                from ..ocr.tesseract import TesseractOcrEngine
                from ..readers.pdf import PdfReader

                reader = PdfReader(
                    ocr_engine=TesseractOcrEngine(
                        language=config.ocr.language,
                        psm=config.ocr.psm,
                    ),
                    ocr_config=config.ocr,
                )
            else:
                reader = ReaderFactory.create(source)

            from ..tts.edge import EdgeTTSEngine

            tts = EdgeTTSEngine(
                voice=config.tts.voice,
                rate=config.tts.rate,
                volume=config.tts.volume,
                pitch=config.tts.pitch,
            )
            pipeline = AudiobookPipeline(reader=reader, tts=tts, config=config)

            def report(progress: float, status_key: str) -> None:
                self._generation_queue.put(("progress", progress, status_key))

            result = asyncio.run(
                pipeline.run(
                    source,
                    output_dir,
                    progress_callback=report,
                )
            )
            self._generation_queue.put(("success", result))
        except Exception as exc:
            self._generation_queue.put(("error", exc))
        finally:
            # The temporary working directory is an implementation detail.
            # Never leave it behind in the user's output folder after a job,
            # whether generation succeeds or fails.
            try:
                temp_dir = config.processing.temp_dir
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except (OSError, PermissionError):
                # Cleanup must never hide the real generation result/error.
                pass

    def _poll_generation_queue(self) -> None:
        """Apply worker results on the Tk main thread."""
        try:
            while True:
                event = self._generation_queue.get_nowait()
                kind = event[0]

                if kind == "progress":
                    progress, status_key = event[1], event[2]
                    self.progress.set(progress)
                    self.progress_value.configure(text=f"{progress:.0f}%")
                    self.status.set(self.i18n.t(status_key))
                    continue

                self._generation_running = False
                self.generate_button.set_enabled(True)

                if kind == "success":
                    result = event[1]
                    if result.merged_file is None:
                        self.status.set(self.i18n.t("status.error"))
                        show_message_dialog(
                            self,
                            self.i18n.t("dialog.error.title"),
                            self.i18n.t("dialog.error.merge_failed"),
                            kind="error",
                        )
                    else:
                        # A completed job no longer represents an active progress
                        # state. Reset the bar immediately so the next audiobook
                        # starts from a clean 0% state.
                        self.progress.set(0)
                        self.progress_value.configure(text="0%")
                        # Start the next job from a completely clean form.
                        # The actual output path remains in result.merged_file;
                        # only the GUI fields are cleared here.
                        self.input_path.set("")
                        self.output_dir.set("")
                        self.status.set(self.i18n.t("status.ready"))
                        show_message_dialog(
                            self,
                            self.i18n.t("dialog.info.title"),
                            self.i18n.t(
                                "dialog.info.generation_complete",
                                path=shorten_path(result.merged_file),
                            ),
                            kind="success",
                        )
                elif kind == "error":
                    exc = event[1]
                    self.status.set(self.i18n.t("status.error"))
                    show_message_dialog(
                        self,
                        self.i18n.t("dialog.error.title"),
                        str(exc) or self.i18n.t("status.error"),
                        kind="error",
                    )

        except queue.Empty:
            pass

        if self._generation_running:
            self.after(100, self._poll_generation_queue)

    def _center_window(self):
        self.update_idletasks()
        width, height = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        try:
            import ctypes
            from ctypes import wintypes
            if hasattr(ctypes, "windll"):
                rect = wintypes.RECT()
                SPI_GETWORKAREA = 0x0030
                if ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
                    work_width = rect.right - rect.left
                    work_height = rect.bottom - rect.top
                    x = rect.left + max(0, (work_width - width) // 2)
                    y = rect.top + max(0, (work_height - height) // 2)
                    self.geometry(f"{width}x{height}+{x}+{y}")
                    return
        except (AttributeError, OSError, TypeError):
            pass
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def run() -> None:
    """Launch the graphical application."""
    app = MainWindow()
    app.mainloop()
