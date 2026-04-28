"""
Execution flow mixin for SimpleTool.
"""

from __future__ import annotations

from typing import Any


class SimpleToolExecutionMixin:
    async def execute(self, arguments: dict[str, Any]) -> list:
        """Execute the simple tool using the comprehensive flow from old base.py.

        This method replicates the proven execution pattern while using SimpleTool
        hooks.
        """
        import json
        import logging

        from mcp.types import TextContent

        from ..models import ToolOutput

        logger = logging.getLogger(f"tools.{self.get_name()}")

        try:
            # Store arguments for access by helper methods
            self._current_arguments = arguments

            logger.info(
                f"🔧 {self.get_name()} tool called with arguments: {list(arguments.keys())}",
            )

            # Validate request using the tool's Pydantic model
            request_model = self.get_request_model()
            request = request_model(**arguments)
            logger.debug(f"Request validation successful for {self.get_name()}")

            # Validate file paths for security
            # This prevents path traversal attacks and ensures proper access control
            path_error = self._validate_file_paths(request)
            if path_error:
                error_output = ToolOutput(
                    status="error",
                    content=path_error,
                    content_type="text",
                )
                return [TextContent(type="text", text=error_output.model_dump_json())]

            # Handle model resolution like old base.py
            model_name = self.get_request_model_name(request)
            if not model_name:
                from pheno.config import DEFAULT_MODEL

                model_name = DEFAULT_MODEL

            # Store the current model name for later use
            self._current_model_name = model_name

            # Handle model context from arguments (for in-process testing)
            if "_model_context" in arguments:
                self._model_context = arguments["_model_context"]
                logger.debug(f"{self.get_name()}: Using model context from arguments")
            else:
                # Create model context if not provided
                from utils.model_context import ModelContext

                self._model_context = ModelContext(model_name)
                logger.debug(f"{self.get_name()}: Created model context for {model_name}")

            # Get images if present
            images = self.get_request_images(request)
            continuation_id = self.get_request_continuation_id(request)

            # Handle conversation history and prompt preparation
            if continuation_id:
                # Check if conversation history is already embedded
                field_value = self.get_request_prompt(request)
                if "=== CONVERSATION HISTORY ===" in field_value:
                    # Use pre-embedded history
                    prompt = field_value
                    logger.debug(f"{self.get_name()}: Using pre-embedded conversation history")
                else:
                    # No embedded history - reconstruct it (for in-process calls)
                    logger.debug(
                        f"{self.get_name()}: No embedded history found, reconstructing conversation",
                    )

                    # Get thread context
                    from utils.conversation_memory import (
                        add_turn,
                        build_conversation_history,
                        get_thread,
                    )

                    thread_context = get_thread(continuation_id)

                    if thread_context:
                        # Add user's new input to conversation
                        user_prompt = self.get_request_prompt(request)
                        user_files = self.get_request_files(request)
                        if user_prompt:
                            add_turn(continuation_id, "user", user_prompt, files=user_files)

                            # Get updated thread context after adding the turn
                            thread_context = get_thread(continuation_id)
                            logger.debug(
                                f"{self.get_name()}: Retrieved updated thread with {len(thread_context.turns)} turns",
                            )

                        # Build conversation history with updated thread context
                        conversation_history, _conversation_tokens = build_conversation_history(
                            thread_context, self._model_context,
                        )

                        # Get the base prompt from the tool
                        base_prompt = await self.prepare_prompt(request)

                        # Combine with conversation history
                        if conversation_history:
                            prompt = (
                                f"{conversation_history}\n\n=== NEW USER INPUT ===\n{base_prompt}"
                            )
                        else:
                            prompt = base_prompt
                    else:
                        # Thread not found, prepare normally
                        logger.warning(
                            f"Thread {continuation_id} not found, preparing prompt normally",
                        )
                        prompt = await self.prepare_prompt(request)
            else:
                # New conversation, prepare prompt normally
                prompt = await self.prepare_prompt(request)

                # Add follow-up instructions for new conversations
                from server import get_follow_up_instructions

                follow_up_instructions = get_follow_up_instructions(0)
                prompt = f"{prompt}\n\n{follow_up_instructions}"
                logger.debug(
                    f"Added follow-up instructions for new {self.get_name()} conversation",
                )  # Validate images if any were provided
            if images:
                image_validation_error = self._validate_image_limits(
                    images, model_context=self._model_context, continuation_id=continuation_id,
                )
                if image_validation_error:
                    return [
                        TextContent(
                            type="text", text=json.dumps(image_validation_error, ensure_ascii=False),
                        ),
                    ]

            # Get and validate temperature against model constraints
            temperature, temp_warnings = self.get_validated_temperature(
                request, self._model_context,
            )

            # Log any temperature corrections
            for warning in temp_warnings:
                logger.warning(warning)

            thinking_mode = self.get_request_thinking_mode(request)
            if thinking_mode is None:
                thinking_mode = self.get_default_thinking_mode()

            # Get the provider from model context (clean OOP - no re-fetching)
            provider = self._model_context.provider
            capabilities = self._model_context.capabilities

            # Get system prompt for this tool
            base_system_prompt = self.get_system_prompt()
            capability_augmented_prompt = self._augment_system_prompt_with_capabilities(
                base_system_prompt, capabilities,
            )
            language_instruction = self.get_language_instruction()
            system_prompt = language_instruction + capability_augmented_prompt

            # Generate AI response using the provider
            logger.info(
                f"Sending request to {provider.get_provider_type().value} API for {self.get_name()}",
            )
            logger.info(
                f"Using model: {self._model_context.model_name} via {provider.get_provider_type().value} provider",
            )

            # Estimate tokens for logging
            from utils.token_utils import estimate_tokens

            estimated_tokens = estimate_tokens(prompt)
            logger.debug(f"Prompt length: {len(prompt)} characters (~{estimated_tokens:,} tokens)")

            # Resolve model capabilities for feature gating
            supports_thinking = capabilities.supports_extended_thinking

            # Generate content with provider abstraction
            model_response = provider.generate_content(
                prompt=prompt,
                model_name=self._current_model_name,
                system_prompt=system_prompt,
                temperature=temperature,
                thinking_mode=thinking_mode if supports_thinking else None,
                images=images if images else None,
            )

            logger.info(
                f"Received response from {provider.get_provider_type().value} API for {self.get_name()}",
            )

            # Process the model's response
            if model_response.content:
                raw_text = model_response.content

                # Create model info for conversation tracking
                model_info = {
                    "provider": provider,
                    "model_name": self._current_model_name,
                    "model_response": model_response,
                }

                # Parse response using the same logic as old base.py
                tool_output = self._parse_response(raw_text, request, model_info)
                logger.info(f"✅ {self.get_name()} tool completed successfully")

            else:
                # Handle cases where the model couldn't generate a response
                metadata = model_response.metadata or {}
                finish_reason = metadata.get("finish_reason", "Unknown")

                if metadata.get("is_blocked_by_safety"):
                    # Specific handling for content safety blocks
                    safety_details = metadata.get("safety_feedback") or "details not provided"
                    logger.warning(
                        f"Response blocked by content safety policy for {self.get_name()}. "
                        f"Reason: {finish_reason}, Details: {safety_details}",
                    )
                    tool_output = ToolOutput(
                        status="error",
                        content="Your request was blocked by the content safety policy. "
                        "Please try modifying your prompt.",
                        content_type="text",
                    )
                # Handle other empty responses - could be legitimate completion or unclear blocking
                elif finish_reason == "STOP":
                    # Model completed normally but returned empty content - retry with clarification
                    logger.info(
                        f"Model completed with empty response for {self.get_name()}, retrying with clarification",
                    )

                    # Retry the same request with modified prompt asking for explicit response
                    original_prompt = prompt
                    retry_prompt = (
                        f"{original_prompt}\n\nIMPORTANT: Please provide a substantive response. "
                        "If you cannot respond to the above request, please explain why and suggest alternatives."
                    )

                    try:
                        retry_response = provider.generate_content(
                            prompt=retry_prompt,
                            model_name=self._current_model_name,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            thinking_mode=thinking_mode if supports_thinking else None,
                            images=images if images else None,
                        )

                        if retry_response.content:
                            # Successful retry - use the retry response
                            logger.info(f"Retry successful for {self.get_name()}")
                            raw_text = retry_response.content

                            # Update model info for the successful retry
                            model_info = {
                                "provider": provider,
                                "model_name": self._current_model_name,
                                "model_response": retry_response,
                            }

                            # Parse the retry response
                            tool_output = self._parse_response(raw_text, request, model_info)
                            logger.info(
                                f"✅ {self.get_name()} tool completed successfully after retry",
                            )
                        else:
                            # Retry also failed - inspect metadata to find out why
                            retry_metadata = retry_response.metadata or {}
                            if retry_metadata.get("is_blocked_by_safety"):
                                # The retry was blocked by safety filters
                                safety_details = (
                                    retry_metadata.get("safety_feedback")
                                    or "details not provided"
                                )
                                logger.warning(
                                    f"Retry for {self.get_name()} was blocked by content safety policy. "
                                    f"Details: {safety_details}",
                                )
                                tool_output = ToolOutput(
                                    status="error",
                                    content="Your request was also blocked by the content safety policy after a retry. "
                                    "Please try rephrasing your prompt significantly.",
                                    content_type="text",
                                )
                            else:
                                # Retry failed for other reasons (e.g., another STOP)
                                tool_output = ToolOutput(
                                    status="error",
                                    content="The model repeatedly returned empty responses. This may indicate content filtering or a model issue.",
                                    content_type="text",
                                )
                    except Exception as retry_error:
                        logger.warning(f"Retry failed for {self.get_name()}: {retry_error}")
                        tool_output = ToolOutput(
                            status="error",
                            content=f"Model returned empty response and retry failed: {retry_error!s}",
                            content_type="text",
                        )
                else:
                    # Non-STOP finish reasons are likely actual errors
                    logger.warning(
                        f"Response blocked or incomplete for {self.get_name()}. Finish reason: {finish_reason}",
                    )
                    tool_output = ToolOutput(
                        status="error",
                        content=f"Response blocked or incomplete. Finish reason: {finish_reason}",
                        content_type="text",
                    )

            # Return the tool output as TextContent
            return [TextContent(type="text", text=tool_output.model_dump_json())]

        except Exception as e:
            # Special handling for MCP size check errors
            if str(e).startswith("MCP_SIZE_CHECK:"):
                # Extract the JSON content after the prefix
                json_content = str(e)[len("MCP_SIZE_CHECK:") :]
                return [TextContent(type="text", text=json_content)]

            logger.exception(f"Error in {self.get_name()}: {e!s}")
            error_output = ToolOutput(
                status="error",
                content=f"Error in {self.get_name()}: {e!s}",
                content_type="text",
            )
            return [TextContent(type="text", text=error_output.model_dump_json())]
