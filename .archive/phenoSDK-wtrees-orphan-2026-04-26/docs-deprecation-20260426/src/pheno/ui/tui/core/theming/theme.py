"""
Theme data structures.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .color_utils import RGBColor
from .palette import ColorPalette
from .tokens import AnimationSettings, SpacingSettings, TypographySettings


@dataclass
class Theme:
    """
    Complete theme definition with palette and design tokens.
    """

    name: str
    palette: ColorPalette
    typography: TypographySettings = field(default_factory=TypographySettings)
    spacing: SpacingSettings = field(default_factory=SpacingSettings)
    animations: AnimationSettings = field(default_factory=AnimationSettings)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "palette": self.palette.to_dict(),
            "typography": asdict(self.typography),
            "spacing": asdict(self.spacing),
            "animations": asdict(self.animations),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Theme:
        palette_data = data.get("palette", {})
        palette = ColorPalette(
            primary=RGBColor.from_hex(palette_data.get("primary", "#000000")),
            secondary=RGBColor.from_hex(palette_data.get("secondary", "#000000")),
            accent=RGBColor.from_hex(palette_data.get("accent", "#000000")),
            background=RGBColor.from_hex(palette_data.get("background", "#ffffff")),
            surface=RGBColor.from_hex(palette_data.get("surface", "#ffffff")),
            text=RGBColor.from_hex(palette_data.get("text", "#000000")),
            text_secondary=RGBColor.from_hex(palette_data.get("text_secondary", "#000000")),
            text_muted=RGBColor.from_hex(palette_data.get("text_muted", "#000000")),
            border=RGBColor.from_hex(palette_data.get("border", "#000000")),
            success=RGBColor.from_hex(palette_data.get("success", "#000000")),
            warning=RGBColor.from_hex(palette_data.get("warning", "#000000")),
            error=RGBColor.from_hex(palette_data.get("error", "#000000")),
            info=RGBColor.from_hex(palette_data.get("info", "#000000")),
        )

        return cls(
            name=data.get("name", "default"),
            palette=palette,
            typography=TypographySettings(**data.get("typography", {})),
            spacing=SpacingSettings(**data.get("spacing", {})),
            animations=AnimationSettings(**data.get("animations", {})),
            metadata=data.get("metadata", {}),
        )


__all__ = ["Theme"]
