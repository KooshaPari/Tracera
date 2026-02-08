"""VHS Tape File Generator for QA Integration system.

Provides a fluent API for generating VHS .tape files programmatically.
VHS (charmbracelet/vhs) uses declarative .tape files to record terminal sessions.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TapeFileGenerator:
    """Fluent API for generating VHS .tape files programmatically.

    VHS uses declarative .tape files to describe terminal recordings.
    This class provides a chainable, type-safe way to generate these files.

    Example:
        tape = (
            TapeFileGenerator()
            .output("demo.gif")
            .set_shell("bash")
            .set_font_size(14)
            .set_width(960)
            .set_height(540)
            .set_theme("Dracula")
            .require("npm")
            .hidden_setup(["cd /path/to/project", "npm install"])
            .type("npm test")
            .enter()
            .wait("Tests:", timeout="120s")
            .sleep(2)
        )
        tape.write("demo.tape")
        # Or get content: tape_content = tape.build()

    See: https://github.com/charmbracelet/vhs
    Run `vhs themes` for available themes.
    """

    _settings: list[str] = field(default_factory=list)
    _requires: list[str] = field(default_factory=list)
    _commands: list[str] = field(default_factory=list)

    # === Output Configuration ===

    def output(self, path: str) -> "TapeFileGenerator":
        """Set output file path.

        Supports formats: .gif, .mp4, .webm, or directory for PNG frames.

        Args:
            path: Output file path (e.g., "demo.gif", "video.mp4")
        """
        self._settings.append(f'Output "{path}"')
        return self

    # === Display Settings ===

    def set_shell(self, shell: str = "bash") -> "TapeFileGenerator":
        """Set the shell to use.

        Args:
            shell: Shell name (bash, zsh, sh, fish). Default "bash".
        """
        self._settings.append(f"Set Shell {shell}")
        return self

    def set_font_size(self, size: int = 14) -> "TapeFileGenerator":
        """Set terminal font size.

        Args:
            size: Font size in pixels. Default 14.
        """
        self._settings.append(f"Set FontSize {size}")
        return self

    def set_font_family(self, family: str = "JetBrains Mono") -> "TapeFileGenerator":
        """Set terminal font family.

        Args:
            family: Font family name. Default "JetBrains Mono".
        """
        self._settings.append(f'Set FontFamily "{family}"')
        return self

    def set_width(self, width: int = 1200) -> "TapeFileGenerator":
        """Set terminal width in pixels.

        Args:
            width: Width in pixels. Default 1200.
        """
        self._settings.append(f"Set Width {width}")
        return self

    def set_height(self, height: int = 600) -> "TapeFileGenerator":
        """Set terminal height in pixels.

        Args:
            height: Height in pixels. Default 600.
        """
        self._settings.append(f"Set Height {height}")
        return self

    def set_theme(self, theme: str = "Dracula") -> "TapeFileGenerator":
        """Set color theme.

        Run `vhs themes` for full list of available themes.

        Popular themes:
        - Dracula
        - Catppuccin Frappe / Latte / Macchiato / Mocha
        - Solarized Dark / Light
        - Nord
        - Gruvbox

        Args:
            theme: Theme name. Default "Dracula".
        """
        self._settings.append(f'Set Theme "{theme}"')
        return self

    def set_padding(self, padding: int = 10) -> "TapeFileGenerator":
        """Set terminal padding in pixels.

        Args:
            padding: Padding in pixels. Default 10.
        """
        self._settings.append(f"Set Padding {padding}")
        return self

    def set_framerate(self, fps: int = 30) -> "TapeFileGenerator":
        """Set output framerate.

        Lower framerates produce smaller files.

        Args:
            fps: Frames per second (10-60). Default 30.
        """
        self._settings.append(f"Set Framerate {fps}")
        return self

    def set_typing_speed(self, speed: str = "50ms") -> "TapeFileGenerator":
        """Set default typing speed.

        Args:
            speed: Time between keystrokes (e.g., "50ms", "100ms"). Default "50ms".
        """
        self._settings.append(f"Set TypingSpeed {speed}")
        return self

    def set_playback_speed(self, speed: float = 1.0) -> "TapeFileGenerator":
        """Set playback speed multiplier.

        Higher values speed up the output (and reduce file size).

        Args:
            speed: Speed multiplier (e.g., 2.0 = 2x faster). Default 1.0.
        """
        self._settings.append(f"Set PlaybackSpeed {speed}")
        return self

    def set_loop_offset(self, seconds: float = 5.0) -> "TapeFileGenerator":
        """Set loop offset for GIF looping.

        The GIF will wait this long before looping.

        Args:
            seconds: Seconds to wait before loop. Default 5.0.
        """
        self._settings.append(f"Set LoopOffset {seconds}")
        return self

    # === Requirements ===

    def require(self, program: str) -> "TapeFileGenerator":
        """Require a program to be in PATH.

        VHS will fail early if the program is not available.

        Args:
            program: Program name (e.g., "npm", "cargo", "python").
        """
        self._requires.append(f"Require {program}")
        return self

    # === Environment ===

    def env(self, key: str, value: str) -> "TapeFileGenerator":
        """Set an environment variable.

        Args:
            key: Environment variable name.
            value: Environment variable value.
        """
        escaped_value = value.replace('"', '\\"')
        self._commands.append(f'Env {key} "{escaped_value}"')
        return self

    def source(self, tape_path: str) -> "TapeFileGenerator":
        """Include commands from another tape file.

        Useful for reusable setup or configuration.

        Args:
            tape_path: Path to another .tape file to include.
        """
        self._commands.append(f'Source "{tape_path}"')
        return self

    # === Text Input ===

    def type(self, text: str, speed: str | None = None) -> "TapeFileGenerator":
        """Type text into the terminal.

        Args:
            text: Text to type.
            speed: Optional speed override (e.g., "100ms", "10ms").
        """
        escaped = text.replace('"', '\\"')
        if speed:
            self._commands.append(f'Type@{speed} "{escaped}"')
        else:
            self._commands.append(f'Type "{escaped}"')
        return self

    def enter(self) -> "TapeFileGenerator":
        """Press Enter key."""
        self._commands.append("Enter")
        return self

    def backspace(self, count: int = 1) -> "TapeFileGenerator":
        """Press Backspace key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Backspace {count}" if count > 1 else "Backspace")
        return self

    def space(self, count: int = 1) -> "TapeFileGenerator":
        """Press Space key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Space {count}" if count > 1 else "Space")
        return self

    def tab(self) -> "TapeFileGenerator":
        """Press Tab key."""
        self._commands.append("Tab")
        return self

    # === Navigation ===

    def up(self, count: int = 1) -> "TapeFileGenerator":
        """Press Up arrow key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Up {count}" if count > 1 else "Up")
        return self

    def down(self, count: int = 1) -> "TapeFileGenerator":
        """Press Down arrow key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Down {count}" if count > 1 else "Down")
        return self

    def left(self, count: int = 1) -> "TapeFileGenerator":
        """Press Left arrow key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Left {count}" if count > 1 else "Left")
        return self

    def right(self, count: int = 1) -> "TapeFileGenerator":
        """Press Right arrow key.

        Args:
            count: Number of times to press. Default 1.
        """
        self._commands.append(f"Right {count}" if count > 1 else "Right")
        return self

    def page_up(self) -> "TapeFileGenerator":
        """Press Page Up key."""
        self._commands.append("PageUp")
        return self

    def page_down(self) -> "TapeFileGenerator":
        """Press Page Down key."""
        self._commands.append("PageDown")
        return self

    def home(self) -> "TapeFileGenerator":
        """Press Home key."""
        self._commands.append("Home")
        return self

    def end(self) -> "TapeFileGenerator":
        """Press End key."""
        self._commands.append("End")
        return self

    def escape(self) -> "TapeFileGenerator":
        """Press Escape key."""
        self._commands.append("Escape")
        return self

    # === Control Keys ===

    def ctrl(self, key: str) -> "TapeFileGenerator":
        """Press Ctrl+key combination.

        Args:
            key: Key to combine with Ctrl (e.g., "C", "A", "L").
        """
        self._commands.append(f"Ctrl+{key}")
        return self

    def alt(self, key: str) -> "TapeFileGenerator":
        """Press Alt+key combination.

        Args:
            key: Key to combine with Alt.
        """
        self._commands.append(f"Alt+{key}")
        return self

    def ctrl_alt(self, key: str) -> "TapeFileGenerator":
        """Press Ctrl+Alt+key combination.

        Args:
            key: Key to combine with Ctrl+Alt.
        """
        self._commands.append(f"Ctrl+Alt+{key}")
        return self

    # === Timing ===

    def sleep(self, seconds: float) -> "TapeFileGenerator":
        """Pause for specified duration.

        Args:
            seconds: Seconds to pause.
        """
        self._commands.append(f"Sleep {seconds}s")
        return self

    def wait(
        self,
        pattern: str | None = None,
        timeout: str | None = None,
        search_screen: bool = False,
    ) -> "TapeFileGenerator":
        """Wait for pattern to appear.

        More reliable than Sleep when waiting for command completion.

        Args:
            pattern: Regex pattern to wait for. Default waits for />$/ prompt.
            timeout: Maximum wait time (e.g., "30s", "2m"). Default 15s.
            search_screen: Search entire screen instead of just last line.

        Examples:
            .wait()  # Wait for default prompt
            .wait("Tests:")  # Wait for "Tests:" on last line
            .wait("error", search_screen=True)  # Wait for "error" anywhere
            .wait("Done", timeout="120s")  # Wait up to 2 minutes
        """
        cmd = "Wait"
        if search_screen:
            cmd += "+Screen"
        if timeout:
            cmd += f"@{timeout}"
        if pattern:
            cmd += f" /{pattern}/"
        self._commands.append(cmd)
        return self

    # === Visibility ===

    def hide(self) -> "TapeFileGenerator":
        """Hide subsequent commands from recording.

        Use this for setup commands that shouldn't appear in the output.
        """
        self._commands.append("Hide")
        return self

    def show(self) -> "TapeFileGenerator":
        """Show subsequent commands in recording.

        Use after hide() to resume showing commands.
        """
        self._commands.append("Show")
        return self

    # === Screenshots ===

    def screenshot(self, filename: str) -> "TapeFileGenerator":
        """Take a screenshot at current point.

        Args:
            filename: Output filename for screenshot.
        """
        self._commands.append(f'Screenshot "{filename}"')
        return self

    # === Clipboard ===

    def copy(self, text: str) -> "TapeFileGenerator":
        """Copy text to clipboard.

        Args:
            text: Text to copy.
        """
        escaped = text.replace('"', '\\"')
        self._commands.append(f'Copy "{escaped}"')
        return self

    def paste(self) -> "TapeFileGenerator":
        """Paste from clipboard."""
        self._commands.append("Paste")
        return self

    # === Build ===

    def build(self) -> str:
        """Generate the complete .tape file content.

        Returns:
            String content of the .tape file.
        """
        lines = []

        # Settings first
        lines.extend(self._settings)
        if self._settings:
            lines.append("")

        # Requirements
        lines.extend(self._requires)
        if self._requires:
            lines.append("")

        # Commands
        lines.extend(self._commands)

        return "\n".join(lines)

    def write(self, path: str | Path) -> Path:
        """Write tape content to file.

        Args:
            path: Path to write .tape file to.

        Returns:
            Path to written file.
        """
        path = Path(path)
        path.write_text(self.build())
        return path

    # === Convenience Methods ===

    def run_command(
        self,
        command: str,
        wait_pattern: str | None = None,
        wait_seconds: float = 1.0,
    ) -> "TapeFileGenerator":
        """Type command, press enter, and wait.

        Convenience method that combines type, enter, and wait/sleep.

        Args:
            command: Command to run.
            wait_pattern: Pattern to wait for (uses wait if provided).
            wait_seconds: Seconds to sleep (used if no wait_pattern).
        """
        self.type(command)
        self.enter()
        if wait_pattern:
            self.wait(wait_pattern)
        else:
            self.sleep(wait_seconds)
        return self

    def hidden_setup(self, commands: list[str]) -> "TapeFileGenerator":
        """Run setup commands hidden from recording.

        Executes commands, clears screen, then resumes recording.

        Args:
            commands: List of shell commands to run hidden.

        Example:
            .hidden_setup(["cd /project", "npm install", "export NODE_ENV=test"])
        """
        self.hide()
        for cmd in commands:
            self.type(cmd)
            self.enter()
        self.type("clear")
        self.enter()
        self.show()
        return self

    def cd(self, directory: str, hidden: bool = True) -> "TapeFileGenerator":
        """Change directory.

        Args:
            directory: Directory to change to.
            hidden: Whether to hide the cd command. Default True.
        """
        if hidden:
            self.hide()
            self.type(f"cd {directory}")
            self.enter()
            self.show()
        else:
            self.type(f"cd {directory}")
            self.enter()
        return self

    def clear(self) -> "TapeFileGenerator":
        """Clear the terminal screen."""
        self.type("clear")
        self.enter()
        return self

    def comment(self, text: str) -> "TapeFileGenerator":
        """Add a comment to the tape file.

        Comments are lines starting with # and are ignored by VHS.

        Args:
            text: Comment text.
        """
        self._commands.append(f"# {text}")
        return self

    def preset_demo(self) -> "TapeFileGenerator":
        """Apply preset settings for demo recordings.

        Sets: bash shell, 14pt font, 960x540, Dracula theme, 30fps.
        """
        return (
            self
            .set_shell("bash")
            .set_font_size(14)
            .set_width(960)
            .set_height(540)
            .set_theme("Dracula")
            .set_framerate(30)
            .set_typing_speed("50ms")
        )

    def preset_test(self) -> "TapeFileGenerator":
        """Apply preset settings for test recordings.

        Sets: bash shell, 14pt font, 1200x600, Catppuccin Frappe theme, 30fps.
        """
        return (
            self
            .set_shell("bash")
            .set_font_size(14)
            .set_width(1200)
            .set_height(600)
            .set_theme("Catppuccin Frappe")
            .set_framerate(30)
            .set_typing_speed("30ms")
        )

    def preset_minimal(self) -> "TapeFileGenerator":
        """Apply preset settings for minimal/small recordings.

        Sets: bash shell, 12pt font, 640x360, Dracula theme, 20fps, 2x speed.
        Good for smaller file sizes.
        """
        return (
            self
            .set_shell("bash")
            .set_font_size(12)
            .set_width(640)
            .set_height(360)
            .set_theme("Dracula")
            .set_framerate(20)
            .set_playback_speed(2.0)
            .set_typing_speed("20ms")
        )
