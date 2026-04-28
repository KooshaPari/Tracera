"""Box drawing utilities for terminal UIs.

Provides box and border drawing functions.
"""


class BoxDrawing:
    """
    Box drawing character sets.
    """

    # Single line box characters
    SINGLE = {
        "tl": "┌",  # top-left
        "tr": "┐",  # top-right
        "bl": "└",  # bottom-left
        "br": "┘",  # bottom-right
        "h": "─",  # horizontal
        "v": "│",  # vertical
        "t": "┬",  # top junction
        "b": "┴",  # bottom junction
        "l": "├",  # left junction
        "r": "┤",  # right junction
        "x": "┼",  # cross junction
    }

    # Double line box characters
    DOUBLE = {
        "tl": "╔",
        "tr": "╗",
        "bl": "╚",
        "br": "╝",
        "h": "═",
        "v": "║",
        "t": "╦",
        "b": "╩",
        "l": "╠",
        "r": "╣",
        "x": "╬",
    }

    # Heavy line box characters
    HEAVY = {
        "tl": "┏",
        "tr": "┓",
        "bl": "┗",
        "br": "┛",
        "h": "━",
        "v": "┃",
        "t": "┳",
        "b": "┻",
        "l": "┣",
        "r": "┫",
        "x": "╋",
    }

    # Rounded box characters
    ROUNDED = {
        "tl": "╭",
        "tr": "╮",
        "bl": "╰",
        "br": "╯",
        "h": "─",
        "v": "│",
        "t": "┬",
        "b": "┴",
        "l": "├",
        "r": "┤",
        "x": "┼",
    }

    @staticmethod
    def get_charset(style: str = "single"):
        """
        Get box drawing character set.
        """
        styles = {
            "single": BoxDrawing.SINGLE,
            "double": BoxDrawing.DOUBLE,
            "heavy": BoxDrawing.HEAVY,
            "rounded": BoxDrawing.ROUNDED,
        }
        return styles.get(style, BoxDrawing.SINGLE)


def draw_box(width: int, height: int, title: str | None = None, style: str = "single") -> str:
    """Draw a box with optional title.

    Args:
        width: Box width
        height: Box height
        title: Optional title text
        style: Box style (single, double, heavy, rounded)

    Returns:
        String representation of the box
    """
    chars = BoxDrawing.get_charset(style)

    lines = []

    # Top border
    if title:
        title_len = len(title) + 2  # Add spaces around title
        left_len = (width - title_len - 2) // 2
        right_len = width - title_len - left_len - 2

        top = (
            chars["tl"]
            + chars["h"] * left_len
            + f" {title} "
            + chars["h"] * right_len
            + chars["tr"]
        )
    else:
        top = chars["tl"] + chars["h"] * (width - 2) + chars["tr"]

    lines.append(top)

    # Middle lines
    for _ in range(height - 2):
        lines.append(chars["v"] + " " * (width - 2) + chars["v"])

    # Bottom border
    bottom = chars["bl"] + chars["h"] * (width - 2) + chars["br"]
    lines.append(bottom)

    return "\n".join(lines)


def draw_border(
    content: str, style: str = "single", title: str | None = None, padding: int = 1,
) -> str:
    """Draw a border around content.

    Args:
        content: Content to wrap
        style: Box style
        title: Optional title
        padding: Padding around content

    Returns:
        Content wrapped in border
    """
    chars = BoxDrawing.get_charset(style)

    # Split content into lines
    content_lines = content.split("\n")

    # Calculate width
    max_width = max(len(line) for line in content_lines) if content_lines else 0
    box_width = max_width + 2 * padding + 2

    lines = []

    # Top border
    if title:
        title_len = len(title) + 2
        left_len = (box_width - title_len - 2) // 2
        right_len = box_width - title_len - left_len - 2

        top = (
            chars["tl"]
            + chars["h"] * left_len
            + f" {title} "
            + chars["h"] * right_len
            + chars["tr"]
        )
    else:
        top = chars["tl"] + chars["h"] * (box_width - 2) + chars["tr"]

    lines.append(top)

    # Padding top
    for _ in range(padding):
        lines.append(chars["v"] + " " * (box_width - 2) + chars["v"])

    # Content
    for line in content_lines:
        padded_line = " " * padding + line.ljust(max_width) + " " * padding
        lines.append(chars["v"] + padded_line + chars["v"])

    # Padding bottom
    for _ in range(padding):
        lines.append(chars["v"] + " " * (box_width - 2) + chars["v"])

    # Bottom border
    bottom = chars["bl"] + chars["h"] * (box_width - 2) + chars["br"]
    lines.append(bottom)

    return "\n".join(lines)
