"""
Banner and Branding Widgets - ASCII art and branded displays.

Ported from zen-mcp-server patterns for general use.
"""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual.widgets import Static


class Banner(Static):
    """ASCII art banner display.

    Features:
    - Centered ASCII art
    - Customizable colors
    - Optional subtitle
    - Border styling

    Example:
        banner = Banner(
            art='''
            ╔═══════════════╗
            ║   MY APP      ║
            ╚═══════════════╝
            ''',
            subtitle="Version 1.0.0"
        )
    """

    DEFAULT_CSS = """
    Banner {
        height: auto;
        padding: 1;
        background: $surface;
    }
    """

    def __init__(self, art: str, subtitle: str | None = None, color: str = "cyan", **kwargs):
        super().__init__(**kwargs)
        self.art = art
        self.subtitle = subtitle
        self.color = color

    def render(self) -> Text:
        """
        Render banner.
        """
        content = Text()
        content.append(self.art, style=self.color)

        if self.subtitle:
            content.append("\n")
            content.append(self.subtitle, style="dim")

        return content


class BrandedPanel(Static):
    """Branded panel with custom styling.

    Features:
    - Custom border styles
    - Brand colors
    - Logo/icon support
    - Themed content

    Example:
        panel = BrandedPanel(
            title="My Application",
            content="Welcome to the dashboard",
            brand_color="bright_blue"
        )
    """

    DEFAULT_CSS = """
    BrandedPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        background: $surface;
    }
    """

    def __init__(
        self,
        title: str,
        content: str = "",
        brand_color: str = "cyan",
        icon: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.brand_color = brand_color
        self.icon = icon

    def render(self) -> Panel:
        """
        Render branded panel.
        """
        text = Text()

        if self.icon:
            text.append(f"{self.icon} ", style=f"bold {self.brand_color}")

        text.append(self.content, style="white")

        return Panel(
            text,
            title=f"[bold {self.brand_color}]{self.title}[/bold {self.brand_color}]",
            border_style=self.brand_color,
        )

    def update_content(self, content: str):
        """
        Update panel content.
        """
        self.content = content
        self.refresh()


def generate_ascii_banner(text: str, style: str = "standard", color: str = "cyan") -> str:
    """Generate ASCII art banner from text.

    Args:
        text: Text to convert to ASCII art
        style: Banner style (standard, box, double_box)
        color: Color for the banner

    Returns:
        ASCII art string

    Example:
        banner = generate_ascii_banner("ZEN", style="box", color="cyan")
    """
    if style == "box":
        width = len(text) + 4
        top = "╔" + "═" * (width - 2) + "╗"
        middle = f"║  {text}  ║"
        bottom = "╚" + "═" * (width - 2) + "╝"
        return f"{top}\n{middle}\n{bottom}"

    if style == "double_box":
        width = len(text) + 6
        top = "╔" + "═" * (width - 2) + "╗"
        empty = "║" + " " * (width - 2) + "║"
        middle = f"║   {text}   ║"
        bottom = "╚" + "═" * (width - 2) + "╝"
        return f"{top}\n{empty}\n{middle}\n{empty}\n{bottom}"

    # standard
    return text


class WelcomeScreen(Static):
    """Welcome screen with banner and info.

    Features:
    - Large ASCII banner
    - Version info
    - Quick start tips
    - Branded styling

    Example:
        welcome = WelcomeScreen(
            app_name="My App",
            version="1.0.0",
            description="Production monitoring dashboard"
        )
    """

    DEFAULT_CSS = """
    WelcomeScreen {
        height: auto;
        padding: 2;
        background: $surface;
        align: center middle;
    }
    """

    def __init__(
        self,
        app_name: str,
        version: str = "",
        description: str = "",
        tips: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.app_name = app_name
        self.version = version
        self.description = description
        self.tips = tips or []

    def render(self) -> Panel:
        """
        Render welcome screen.
        """
        content = Text()

        # Banner
        banner = generate_ascii_banner(self.app_name, style="double_box")
        content.append(banner, style="bold cyan")
        content.append("\n\n")

        # Version
        if self.version:
            content.append(f"Version {self.version}", style="dim")
            content.append("\n")

        # Description
        if self.description:
            content.append("\n")
            content.append(self.description, style="white")
            content.append("\n")

        # Tips
        if self.tips:
            content.append("\n")
            content.append("Quick Start:", style="bold yellow")
            content.append("\n")
            for tip in self.tips:
                content.append(f"  • {tip}\n", style="dim")

        return Panel(Align.center(content), border_style="cyan", padding=(1, 2))


class StatusBanner(Static):
    """Status banner for top of dashboard.

    Features:
    - App name and status
    - Uptime display
    - Quick stats
    - Color-coded health

    Example:
        banner = StatusBanner(
            app_name="Production Server",
            status="running",
            uptime="2h 15m",
            stats={"Requests": "1,234", "Errors": "0"}
        )
    """

    DEFAULT_CSS = """
    StatusBanner {
        height: 3;
        background: $accent;
        color: $text;
        padding: 0 2;
    }
    """

    def __init__(
        self,
        app_name: str,
        status: str = "unknown",
        uptime: str = "",
        stats: dict[str, str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.app_name = app_name
        self.status = status
        self.uptime = uptime
        self.stats = stats or {}

    def render(self) -> Text:
        """
        Render status banner.
        """
        content = Text()

        # App name
        content.append(f"⚡ {self.app_name}", style="bold bright_white")
        content.append(" | ", style="dim")

        # Status
        status_colors = {
            "running": "bright_green",
            "stopped": "bright_red",
            "starting": "bright_yellow",
            "error": "bright_red",
        }
        color = status_colors.get(self.status, "white")
        content.append(f"● {self.status.upper()}", style=f"bold {color}")

        # Uptime
        if self.uptime:
            content.append(" | ", style="dim")
            content.append(f"⏱ {self.uptime}", style="cyan")

        # Stats
        for key, value in self.stats.items():
            content.append(" | ", style="dim")
            content.append(f"{key}: {value}", style="white")

        return content

    def update_status(self, status: str, uptime: str = "", stats: dict[str, str] | None = None):
        """
        Update banner status.
        """
        self.status = status
        if uptime:
            self.uptime = uptime
        if stats:
            self.stats = stats
        self.refresh()
