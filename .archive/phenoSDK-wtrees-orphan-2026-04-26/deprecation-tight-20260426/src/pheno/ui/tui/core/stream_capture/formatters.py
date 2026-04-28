"""
Helpers for beautifying captured output.
"""

from __future__ import annotations

import json
import re

from .rich_support import HAS_RICH, Console, Syntax, Text


class OutputFormatter:
    JSON_PATTERN = re.compile(r"^\s*[\{\[].*[\}\]]\s*$")
    KEY_VALUE_PATTERN = re.compile(r"(\w+)=([^\s]+)")
    EXCEPTION_PATTERN = re.compile(r"(Traceback|File \".*\", line \d+|Error:|Exception:)")
    URL_PATTERN = re.compile(r"https?://[^\s]+")

    @staticmethod
    def detect_format(text: str) -> str:
        stripped = text.strip()
        if OutputFormatter.JSON_PATTERN.match(stripped):
            return "json"
        if OutputFormatter.EXCEPTION_PATTERN.search(text):
            return "exception"
        if len(OutputFormatter.KEY_VALUE_PATTERN.findall(text)) >= 2:
            return "structured"
        if OutputFormatter.URL_PATTERN.search(text):
            return "url"
        return "plain"

    @staticmethod
    def format_json(text: str) -> str:
        if not HAS_RICH:
            return text
        try:
            parsed = json.loads(text)
        except Exception:
            return text

        formatted = json.dumps(parsed, indent=2)
        syntax = Syntax(formatted, "json", theme="monokai", line_numbers=False)
        console = Console()
        with console.capture() as capture:
            console.print(syntax)
        return capture.get()

    @staticmethod
    def format_exception(text: str) -> Text | str:
        if not HAS_RICH:
            return text

        output = Text()
        for line in text.split("\n"):
            if line.startswith("Traceback"):
                output.append(line + "\n", style="bold red")
            elif 'File "' in line:
                output.append(line + "\n", style="cyan")
            elif "Error:" in line or "Exception:" in line:
                output.append(line + "\n", style="bold red")
            else:
                output.append(line + "\n")
        return output

    @staticmethod
    def format_structured(text: str) -> Text | str:
        if not HAS_RICH:
            return text

        output = Text()
        for part in text.split():
            if "=" in part:
                key, value = part.split("=", 1)
                output.append(key, style="cyan")
                output.append("=", style="dim")
                output.append(value, style="green")
                output.append(" ")
            else:
                output.append(part + " ")
        return output

    @staticmethod
    def highlight_urls(text: str) -> Text | str:
        if not HAS_RICH:
            return text

        output = Text()
        last_end = 0
        for match in OutputFormatter.URL_PATTERN.finditer(text):
            output.append(text[last_end : match.start()])
            output.append(match.group(), style="blue underline")
            last_end = match.end()
        output.append(text[last_end:])
        return output


__all__ = ["OutputFormatter"]
