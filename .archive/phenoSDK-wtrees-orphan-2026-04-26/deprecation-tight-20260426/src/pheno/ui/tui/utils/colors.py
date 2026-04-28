"""Color utilities for TUI applications.

Provides color manipulation and conversion functions.
"""


class ColorUtils:
    """
    Color manipulation utilities.
    """

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        """
        hex_color = hex_color.lstrip("#")

        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """
        Convert RGB to hex color.
        """
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def darken(hex_color: str, factor: float = 0.2) -> str:
        """
        Darken a color by factor (0-1).
        """
        r, g, b = ColorUtils.hex_to_rgb(hex_color)

        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))

        return ColorUtils.rgb_to_hex(r, g, b)

    @staticmethod
    def lighten(hex_color: str, factor: float = 0.2) -> str:
        """
        Lighten a color by factor (0-1).
        """
        r, g, b = ColorUtils.hex_to_rgb(hex_color)

        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        return ColorUtils.rgb_to_hex(r, g, b)

    @staticmethod
    def is_light(hex_color: str) -> bool:
        """
        Determine if color is light or dark.
        """
        r, g, b = ColorUtils.hex_to_rgb(hex_color)

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

        return luminance > 0.5

    @staticmethod
    def contrast_color(hex_color: str) -> str:
        """
        Get contrasting color (black or white).
        """
        return "#000000" if ColorUtils.is_light(hex_color) else "#ffffff"

    @staticmethod
    def blend(color1: str, color2: str, factor: float = 0.5) -> str:
        """
        Blend two colors together.
        """
        r1, g1, b1 = ColorUtils.hex_to_rgb(color1)
        r2, g2, b2 = ColorUtils.hex_to_rgb(color2)

        r = int(r1 * (1 - factor) + r2 * factor)
        g = int(g1 * (1 - factor) + g2 * factor)
        b = int(b1 * (1 - factor) + b2 * factor)

        return ColorUtils.rgb_to_hex(r, g, b)


# Convenience functions
def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.
    """
    return ColorUtils.hex_to_rgb(hex_color)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB to hex color.
    """
    return ColorUtils.rgb_to_hex(r, g, b)


def darken(hex_color: str, factor: float = 0.2) -> str:
    """
    Darken a color.
    """
    return ColorUtils.darken(hex_color, factor)


def lighten(hex_color: str, factor: float = 0.2) -> str:
    """
    Lighten a color.
    """
    return ColorUtils.lighten(hex_color, factor)
