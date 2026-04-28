"""
Validation helpers for SimpleTool.
"""

from __future__ import annotations


class SimpleToolValidationMixin:
    def get_actually_processed_files(self) -> list:
        """Get actually processed files.

        Override for custom file tracking.
        """
        try:
            return self._actually_processed_files
        except AttributeError:
            return []

    def _validate_file_paths(self, request) -> str | None:
        """Validate that all file paths in the request are absolute paths.

        This is a security measure to prevent path traversal attacks and ensure
        proper access control. All file paths must be absolute (starting with '/').

        Args:
            request: The validated request object

        Returns:
            Optional[str]: Error message if validation fails, None if all paths are valid
        """
        import os

        # Check if request has 'files' attribute (used by most tools)
        files = self.get_request_files(request)
        if files:
            for file_path in files:
                if not os.path.isabs(file_path):
                    return (
                        "Error: All file paths must be FULL absolute paths to real files / folders - DO NOT SHORTEN. "
                        f"Received relative path: {file_path}\n"
                        "Please provide the full absolute path starting with '/' (must be FULL absolute paths to real files / folders - DO NOT SHORTEN)"
                    )

        return None
