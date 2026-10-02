"""Small image effects used by the GUI."""

from PIL import Image, ImageFilter


def add_shadow(
    image: Image.Image,
    offset: tuple[int, int] = (2, 2),
    shadow_color: tuple[int, int, int, int] = (0, 0, 0, 128),
    blur_radius: int = 3,
    border: int = 5,
) -> Image.Image:
    """Return an RGBA image with a soft drop shadow.

    This follows the same rendering approach used by the supplied Transcribe
    project: the source alpha channel becomes the shadow mask, the shadow is
    blurred, and the original image is composited above it.
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    total_width = image.width + abs(offset[0]) + 2 * border
    total_height = image.height + abs(offset[1]) + 2 * border
    result = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    shadow_layer = Image.new("RGBA", image.size, shadow_color)
    result.paste(
        shadow_layer,
        (border + offset[0], border + offset[1]),
        image.getchannel("A"),
    )
    result = result.filter(ImageFilter.GaussianBlur(blur_radius))
    result.paste(image, (border, border), image)
    return result
