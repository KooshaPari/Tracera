"""
Prompt preparation helpers for SimpleTool.
"""

from __future__ import annotations


class SimpleToolPromptMixin:
    def build_standard_prompt(
        self,
        system_prompt: str,
        user_content: str,
        request,
        file_context_title: str = "CONTEXT FILES",
    ) -> str:
        """Build a standard prompt with system prompt, user content, and optional files.

        This is a convenience method that handles the common pattern of:
        1. Adding file content if present
        2. Checking token limits
        3. Adding web search instructions
        4. Combining everything into a well-formatted prompt

        Args:
            system_prompt: The system prompt for the tool
            user_content: The main user request/content
            request: The validated request object
            file_context_title: Title for the file context section

        Returns:
            Complete formatted prompt ready for the AI model
        """
        # Check size limits against raw user input before enriching with internal context
        content_to_validate = self.get_prompt_content_for_size_validation(user_content)
        self._validate_token_limit(content_to_validate, "Content")

        # Add context files if provided (does not affect MCP boundary enforcement)
        files = self.get_request_files(request)
        if files:
            file_content, processed_files = self._prepare_file_content_for_prompt(
                files,
                self.get_request_continuation_id(request),
                "Context files",
                model_context=getattr(self, "_model_context", None),
            )
            self._actually_processed_files = processed_files
            if file_content:
                user_content = f"{user_content}\n\n=== {file_context_title} ===\n{file_content}\n=== END CONTEXT ===="

        # Add standardized web search guidance
        websearch_instruction = self.get_websearch_instruction(self.get_websearch_guidance())

        # Combine system prompt with user content
        return f"""{system_prompt}{websearch_instruction}

=== USER REQUEST ===
{user_content}
=== END REQUEST ===

Please provide a thoughtful, comprehensive response:"""


    def get_prompt_content_for_size_validation(self, user_content: str) -> str:
        """Override to use original user prompt for size validation when conversation
        history is embedded.

        When server.py embeds conversation history into the prompt field, it also stores
        the original user prompt in _original_user_prompt. We use that for size validation
        to avoid incorrectly triggering size limits due to conversation history.

        Args:
            user_content: The user content (may include conversation history)

        Returns:
            The original user prompt if available, otherwise the full user content
        """
        # Check if we have the current arguments from execute() method
        current_args = getattr(self, "_current_arguments", None)
        if current_args:
            # If server.py embedded conversation history, it stores original prompt separately
            original_user_prompt = current_args.get("_original_user_prompt")
            if original_user_prompt is not None:
                # Use original user prompt for size validation (excludes conversation history)
                return original_user_prompt

        # Fallback to default behavior (validate full user content)
        return user_content

    def get_websearch_guidance(self) -> str | None:
        """Return tool-specific web search guidance.

        Override this to provide tool-specific guidance for when web searches
        would be helpful. Return None to use the default guidance.

        Returns:
            Tool-specific web search guidance or None for default
        """
        return None

    def handle_prompt_file_with_fallback(self, request) -> str:
        """Handle prompt.txt files with fallback to request field.

        This is a convenience method for tools that accept prompts either
        as a field or as a prompt.txt file. It handles the extraction
        and validation automatically.

        Args:
            request: The validated request object

        Returns:
            The effective prompt content

        Raises:
            ValueError: If prompt is too large for MCP transport
        """
        # Check for prompt.txt in files
        files = self.get_request_files(request)
        if files:
            prompt_content, updated_files = self.handle_prompt_file(files)

            # Update request files list if needed
            if updated_files is not None:
                self.set_request_files(request, updated_files)
        else:
            prompt_content = None

        # Use prompt.txt content if available, otherwise use the prompt field
        user_content = prompt_content if prompt_content else self.get_request_prompt(request)

        # Check user input size at MCP transport boundary (excluding conversation history)
        validation_content = self.get_prompt_content_for_size_validation(user_content)
        size_check = self.check_prompt_size(validation_content)
        if size_check:
            from ..models import ToolOutput

            raise ValueError(f"MCP_SIZE_CHECK:{ToolOutput(**size_check).model_dump_json()}")

        return user_content

    def get_chat_style_websearch_guidance(self) -> str:
        """Get Chat tool-style web search guidance.

        Returns web search guidance that matches the original Chat tool pattern.
        This is useful for tools that want to maintain the same search behavior.

        Returns:
            Web search guidance text
        """
        return """When discussing topics, consider if searches for these would help:
- Documentation for any technologies or concepts mentioned
- Current best practices and patterns
- Recent developments or updates
- Community discussions and solutions"""

    def prepare_chat_style_prompt(self, request, system_prompt: str | None = None) -> str:
        """Prepare a prompt using Chat tool-style patterns.

        This convenience method replicates the Chat tool's prompt preparation logic:
        1. Handle prompt.txt file if present
        2. Add file context with specific formatting
        3. Add web search guidance
        4. Format with system prompt

        Args:
            request: The validated request object
            system_prompt: System prompt to use (uses get_system_prompt() if None)

        Returns:
            Complete formatted prompt
        """
        # Use provided system prompt or get from tool
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # Get user content (handles prompt.txt files)
        user_content = self.handle_prompt_file_with_fallback(request)

        # Build standard prompt with Chat-style web search guidance
        websearch_guidance = self.get_chat_style_websearch_guidance()

        # Override the websearch guidance temporarily
        original_guidance = self.get_websearch_guidance
        self.get_websearch_guidance = lambda: websearch_guidance

        try:
            full_prompt = self.build_standard_prompt(
                system_prompt, user_content, request, "CONTEXT FILES",
            )
        finally:
            # Restore original guidance method
            self.get_websearch_guidance = original_guidance

        if system_prompt:
            marker = "\n\n=== USER REQUEST ===\n"
            if marker in full_prompt:
                _, user_section = full_prompt.split(marker, 1)
                return f"=== USER REQUEST ===\n{user_section}"

        return full_prompt
