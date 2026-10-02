"""Image loading, scaling and caching for the GUI."""

from pathlib import Path
import tkinter as tk
from typing import Optional

from PIL import Image, ImageTk

from .image_enhancer import add_shadow


class ImageManager:
    """Centralize GUI image resources and render them at the current DPI."""

    def __init__(
        self,
        root: tk.Misc,
        images_dir: Optional[Path] = None,
        scale: float | None = None,
    ) -> None:
        self.root = root
        self.images_dir = images_dir or self._default_images_dir()
        self.scale = max(1.0, float(scale)) if scale is not None else self._dpi_scale()
        self._cache: dict[tuple[str, int, int, float, bool], ImageTk.PhotoImage] = {}

    @staticmethod
    def _default_images_dir() -> Path:
        return Path(__file__).resolve().parents[2] / "assets" / "images"

    def _dpi_scale(self) -> float:
        try:
            return max(1.0, float(self.root.winfo_fpixels("1i")) / 96.0)
        except Exception:
            return 1.0

    def load(
        self,
        filename: str,
        width: int | None = None,
        height: int | None = None,
        *,
        enhance: bool = False,
    ) -> ImageTk.PhotoImage:
        """Load an image at a DPI-aware physical resolution.

        Requested dimensions remain the application's logical dimensions.
        The source artwork is rendered at ``logical_size * DPI_scale`` so
        Windows/Tk do not have to enlarge a low-resolution bitmap. High-
        resolution PNG masters are preferred whenever available.
        """
        path = self.images_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"GUI image not found: {path}")

        master_path = self.images_dir / "png_master" / filename
        source_path = master_path if master_path.is_file() else path

        if width is None or height is None:
            with Image.open(source_path) as image:
                width, height = image.size

        logical_width = int(width)
        logical_height = int(height)
        key = (
            filename,
            logical_width,
            logical_height,
            round(self.scale, 4),
            bool(enhance),
        )
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        physical_width = max(1, round(logical_width * self.scale))
        physical_height = max(1, round(logical_height * self.scale))

        with Image.open(source_path) as image:
            image = image.convert("RGBA")
            image.thumbnail(
                (physical_width, physical_height),
                Image.Resampling.LANCZOS,
            )

            if enhance:
                if max(image.width, image.height) < 100:
                    image = add_shadow(
                        image,
                        offset=(1, 1),
                        blur_radius=2,
                        border=3,
                    )
                else:
                    image = add_shadow(
                        image,
                        offset=(2, 2),
                        blur_radius=3,
                        border=5,
                    )

            photo = ImageTk.PhotoImage(image, master=self.root)

        self._cache[key] = photo
        return photo
