"""
RGB color representation with utility methods and WCAG compliance.
"""

import colorsys
from dataclasses import dataclass

from .wcag_compliance import WCAGLevel


@dataclass
class RGBColor:
    """
    RGB color representation with utility methods.
    """

    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255

    @classmethod
    def from_hex(cls, hex_color: str) -> RGBColor:
        """
        Create RGB color from hex string.
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return cls(r, g, b)

    def to_hex(self) -> str:
        """
        Convert to hex string.
        """
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_hsl(self) -> tuple[float, float, float]:
        """
        Convert to HSL (hue, saturation, lightness).
        """
        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        return colorsys.rgb_to_hls(r, g, b)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> RGBColor:
        """
        Create RGB color from HSL values.
        """
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return cls(int(r * 255), int(g * 255), int(b * 255))

    def luminance(self) -> float:
        """Calculate relative luminance according to WCAG.

        Returns:
            float: Relative luminance (0-1)
        """

        def _channel_luminance(channel: int) -> float:
            c = channel / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r_lum = _channel_luminance(self.r)
        g_lum = _channel_luminance(self.g)
        b_lum = _channel_luminance(self.b)

        return 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum

    def contrast_ratio(self, other: RGBColor) -> float:
        """Calculate WCAG contrast ratio between two colors.

        Args:
            other: Color to compare against

        Returns:
            float: Contrast ratio (1-21)
        """
        l1 = self.luminance()
        l2 = other.luminance()

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def meets_wcag(self, background: RGBColor, level: WCAGLevel) -> bool:
        """Check if color meets WCAG contrast requirements.

        Args:
            background: Background color
            level: WCAG level to check

        Returns:
            bool: True if contrast meets requirements
        """
        ratio = self.contrast_ratio(background)
        return ratio >= level.value

    def lighten(self, amount: float) -> RGBColor:
        """
        Lighten color by amount (0-1).
        """
        h, s, l = self.to_hsl()
        l = min(1.0, l + amount)
        return RGBColor.from_hsl(h, s, l)

    def darken(self, amount: float) -> RGBColor:
        """
        Darken color by amount (0-1).
        """
        h, s, l = self.to_hsl()
        l = max(0.0, l - amount)
        return RGBColor.from_hsl(h, s, l)

    def saturate(self, amount: float) -> RGBColor:
        """
        Increase saturation by amount (0-1).
        """
        h, s, l = self.to_hsl()
        s = min(1.0, s + amount)
        return RGBColor.from_hsl(h, s, l)

    def desaturate(self, amount: float) -> RGBColor:
        """
        Decrease saturation by amount (0-1).
        """
        h, s, l = self.to_hsl()
        s = max(0.0, s - amount)
        return RGBColor.from_hsl(h, s, l)

    def rotate_hue(self, degrees: float) -> RGBColor:
        """
        Rotate hue by degrees.
        """
        h, s, l = self.to_hsl()
        h = (h + degrees / 360.0) % 1.0
        return RGBColor.from_hsl(h, s, l)

    def blend(self, other: RGBColor, amount: float = 0.5) -> RGBColor:
        """
        Blend with another color.
        """
        r = int(self.r * (1 - amount) + other.r * amount)
        g = int(self.g * (1 - amount) + other.g * amount)
        b = int(self.b * (1 - amount) + other.b * amount)
        return RGBColor(r, g, b)
