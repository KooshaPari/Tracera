"""
Conversation and continuation helpers for SimpleTool.
"""

from __future__ import annotations


class SimpleToolConversationMixin:
    def _parse_response(self, raw_text: str, request, model_info: dict | None = None):
        """Parse the raw response and format it using the hook method.

        This simplified version focuses on the SimpleTool pattern: format the response
        using the format_response hook, then handle conversation continuation.
        """
        from ..models import ToolOutput

        # Format the response using the hook method
        formatted_response = self.format_response(raw_text, request, model_info)

        # Handle conversation continuation like old base.py
        continuation_id = self.get_request_continuation_id(request)
        if continuation_id:
            self._record_assistant_turn(continuation_id, raw_text, request, model_info)

        # Create continuation offer like old base.py
        continuation_data = self._create_continuation_offer(request, model_info)
        if continuation_data:
            return self._create_continuation_offer_response(
                formatted_response, continuation_data, request, model_info,
            )
        # Build metadata with model and provider info for success response
        metadata = {}
        if model_info:
            model_name = model_info.get("model_name")
            if model_name:
                metadata["model_used"] = model_name
            provider = model_info.get("provider")
            if provider:
                # Handle both provider objects and string values
                if isinstance(provider, str):
                    metadata["provider_used"] = provider
                else:
                    try:
                        metadata["provider_used"] = provider.get_provider_type().value
                    except AttributeError:
                        # Fallback if provider doesn't have get_provider_type method
                        metadata["provider_used"] = str(provider)

        return ToolOutput(
            status="success",
            content=formatted_response,
            content_type="text",
            metadata=metadata if metadata else None,
        )

    def _create_continuation_offer(self, request, model_info: dict | None = None):
        """
        Create continuation offer following old base.py pattern.
        """
        continuation_id = self.get_request_continuation_id(request)

        try:
            from utils.conversation_memory import create_thread, get_thread

            if continuation_id:
                # Existing conversation
                thread_context = get_thread(continuation_id)
                if thread_context and thread_context.turns:
                    turn_count = len(thread_context.turns)
                    from utils.conversation_memory import MAX_CONVERSATION_TURNS

                    if turn_count >= MAX_CONVERSATION_TURNS - 1:
                        return None  # No more turns allowed

                    remaining_turns = MAX_CONVERSATION_TURNS - turn_count - 1
                    return {
                        "continuation_id": continuation_id,
                        "remaining_turns": remaining_turns,
                        "note": f"You can continue this conversation for {remaining_turns} more exchanges.",
                    }
            else:
                # New conversation - create thread and offer continuation
                # Convert request to dict for initial_context
                initial_request_dict = self.get_request_as_dict(request)

                new_thread_id = create_thread(
                    tool_name=self.get_name(), initial_request=initial_request_dict,
                )

                # Add the initial user turn to the new thread
                from utils.conversation_memory import MAX_CONVERSATION_TURNS, add_turn

                user_prompt = self.get_request_prompt(request)
                user_files = self.get_request_files(request)
                user_images = self.get_request_images(request)

                # Add user's initial turn
                add_turn(
                    new_thread_id,
                    "user",
                    user_prompt,
                    files=user_files,
                    images=user_images,
                    tool_name=self.get_name(),
                )

                return {
                    "continuation_id": new_thread_id,
                    "remaining_turns": MAX_CONVERSATION_TURNS - 1,
                    "note": f"You can continue this conversation for {MAX_CONVERSATION_TURNS - 1} more exchanges.",
                }
        except Exception:
            return None

    def _create_continuation_offer_response(
        self, content: str, continuation_data: dict, request, model_info: dict | None = None,
    ):
        """
        Create response with continuation offer following old base.py pattern.
        """
        from ..models import ContinuationOffer, ToolOutput

        try:
            if not self.get_request_continuation_id(request):
                self._record_assistant_turn(
                    continuation_data["continuation_id"],
                    content,
                    request,
                    model_info,
                )

            continuation_offer = ContinuationOffer(
                continuation_id=continuation_data["continuation_id"],
                note=continuation_data["note"],
                remaining_turns=continuation_data["remaining_turns"],
            )

            # Build metadata with model and provider info
            metadata = {"tool_name": self.get_name(), "conversation_ready": True}
            if model_info:
                model_name = model_info.get("model_name")
                if model_name:
                    metadata["model_used"] = model_name
                provider = model_info.get("provider")
                if provider:
                    # Handle both provider objects and string values
                    if isinstance(provider, str):
                        metadata["provider_used"] = provider
                    else:
                        try:
                            metadata["provider_used"] = provider.get_provider_type().value
                        except AttributeError:
                            # Fallback if provider doesn't have get_provider_type method
                            metadata["provider_used"] = str(provider)

            return ToolOutput(
                status="continuation_available",
                content=content,
                content_type="text",
                continuation_offer=continuation_offer,
                metadata=metadata,
            )
        except Exception:
            # Fallback to simple success if continuation offer fails
            return ToolOutput(status="success", content=content, content_type="text")

    def _record_assistant_turn(
        self, continuation_id: str, response_text: str, request, model_info: dict | None,
    ) -> None:
        """
        Persist an assistant response in conversation memory.
        """

        if not continuation_id:
            return

        from utils.conversation_memory import add_turn

        model_provider = None
        model_name = None
        model_metadata = None

        if model_info:
            provider = model_info.get("provider")
            if provider:
                if isinstance(provider, str):
                    model_provider = provider
                else:
                    try:
                        model_provider = provider.get_provider_type().value
                    except AttributeError:
                        model_provider = str(provider)
            model_name = model_info.get("model_name")
            model_response = model_info.get("model_response")
            if model_response:
                model_metadata = {
                    "usage": model_response.usage,
                    "metadata": model_response.metadata,
                }

        add_turn(
            continuation_id,
            "assistant",
            response_text,
            files=self.get_request_files(request),
            images=self.get_request_images(request),
            tool_name=self.get_name(),
            model_provider=model_provider,
            model_name=model_name,
            model_metadata=model_metadata,
        )
