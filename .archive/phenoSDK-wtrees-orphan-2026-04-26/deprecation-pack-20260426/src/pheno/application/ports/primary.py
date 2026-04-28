"""
Primary port definitions (driving/inbound adapters).
"""

from typing import Any, Protocol


class CommandHandler(Protocol):
    """Command handler protocol for CQRS pattern.

    Commands are requests to change state. Primary adapters (CLI, API, MCP) use this to
    execute commands.
    """

    async def handle(self, command: Any) -> Any:
        """Handle a command.

        Args:
            command: Command object

        Returns:
            Command result

        Raises:
            CommandHandlerError: If command handling fails
        """
        ...


class CLIHandler(Protocol):
    """CLI handler protocol.

    Defines the contract for CLI command handlers.
    """

    async def execute(
        self,
        command: str,
        args: list[str],
        options: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a CLI command.

        Args:
            command: Command name
            args: Positional arguments
            options: Named options/flags

        Returns:
            Command result dictionary

        Raises:
            CLIError: If command execution fails
        """
        ...

    def get_help(self, command: str | None = None) -> str:
        """Get help text for a command.

        Args:
            command: Command name (optional, returns general help if None)

        Returns:
            Help text
        """
        ...

    def list_commands(self) -> list[str]:
        """List all available commands.

        Returns:
            List of command names
        """
        ...


class APIHandler(Protocol):
    """API handler protocol.

    Defines the contract for REST/GraphQL API handlers.
    """

    async def handle_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        body: dict[str, Any] | None = None,
        query_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Handle an API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: Request path
            headers: Request headers
            body: Request body (optional)
            query_params: Query parameters (optional)

        Returns:
            Response dictionary with status, headers, body

        Raises:
            APIError: If request handling fails
        """
        ...

    def get_openapi_spec(self) -> dict[str, Any]:
        """Get OpenAPI specification.

        Returns:
            OpenAPI spec dictionary
        """
        ...


class MCPServerHandler(Protocol):
    """MCP (Model Context Protocol) server handler protocol.

    Defines the contract for MCP server implementations.
    """

    async def handle_resource_request(
        self,
        _resource_uri: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a resource request.

        Args:
            resource_uri: Resource URI
            params: Request parameters (optional)

        Returns:
            Resource data

        Raises:
            MCPError: If request handling fails
        """
        ...

    async def handle_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle a tool call.

        Args:
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            MCPError: If tool call fails
        """
        ...

    async def handle_prompt_request(
        self,
        prompt_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> str:
        """Handle a prompt request.

        Args:
            prompt_name: Prompt name
            arguments: Prompt arguments (optional)

        Returns:
            Prompt text

        Raises:
            MCPError: If prompt request fails
        """
        ...

    def list_resources(self) -> list[dict[str, Any]]:
        """List available resources.

        Returns:
            List of resource metadata
        """
        ...

    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools.

        Returns:
            List of tool metadata
        """
        ...

    def list_prompts(self) -> list[dict[str, Any]]:
        """List available prompts.

        Returns:
            List of prompt metadata
        """
        ...


class EventListenerHandler(Protocol):
    """Event listener handler protocol.

    Defines the contract for handling external events (webhooks, message queues).
    """

    async def handle_webhook(
        self,
        source: str,
        event_type: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Handle a webhook event.

        Args:
            source: Event source (e.g., "github", "stripe")
            event_type: Event type
            payload: Event payload
            headers: Request headers

        Returns:
            Response dictionary

        Raises:
            WebhookError: If webhook handling fails
        """
        ...

    async def handle_queue_message(
        self,
        _queue_name: str,
        message: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Handle a message queue event.

        Args:
            queue_name: Queue name
            message: Message payload
            metadata: Message metadata (optional)

        Raises:
            QueueError: If message handling fails
        """
        ...

    def register_webhook(
        self,
        source: str,
        event_type: str,
        url: str,
        secret: str | None = None,
    ) -> str:
        """Register a webhook.

        Args:
            source: Event source
            event_type: Event type to subscribe to
            url: Webhook URL
            secret: Webhook secret for verification (optional)

        Returns:
            Webhook ID

        Raises:
            WebhookRegistrationError: If registration fails
        """
        ...


class ScheduledTaskHandler(Protocol):
    """Scheduled task handler protocol.

    Defines the contract for handling scheduled/cron tasks.
    """

    async def execute_task(
        self,
        _task_name: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a scheduled task.

        Args:
            task_name: Task name
            params: Task parameters (optional)

        Returns:
            Task result

        Raises:
            TaskExecutionError: If task execution fails
        """
        ...

    def register_task(
        self,
        _task_name: str,
        schedule: str,
        enabled: bool = True,
    ) -> str:
        """Register a scheduled task.

        Args:
            task_name: Task name
            schedule: Cron schedule expression
            enabled: Whether task is enabled (default: True)

        Returns:
            Task ID

        Raises:
            TaskRegistrationError: If registration fails
        """
        ...

    def list_tasks(self) -> list[dict[str, Any]]:
        """List all scheduled tasks.

        Returns:
            List of task metadata
        """
        ...

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get task execution status.

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        ...
