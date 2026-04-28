"""
External service port definitions.
"""

from typing import Protocol

from pheno.domain.value_objects import Email


class EmailService(Protocol):
    """Email service protocol.

    Defines the contract for sending emails. Adapters can implement this for different
    email providers (SendGrid, AWS SES, SMTP, etc.).
    """

    async def send_email(
        self,
        _to: Email,
        subject: str,
        body: str,
        html: str | None = None,
        _from_email: Email | None = None,
    ) -> None:
        """Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html: HTML email body (optional)
            from_email: Sender email address (optional)

        Raises:
            EmailSendError: If sending fails
        """
        ...

    async def send_batch(
        self,
        _emails: list[dict[str, any]],
    ) -> None:
        """Send multiple emails.

        Args:
            emails: List of email dictionaries with to, subject, body, etc.

        Raises:
            EmailSendError: If sending fails
        """
        ...

    async def verify_email(self, email: Email) -> bool:
        """Verify if an email address is valid.

        Args:
            email: Email address to verify

        Returns:
            True if email is valid, False otherwise
        """
        ...


class NotificationService(Protocol):
    """Notification service protocol.

    Defines the contract for sending notifications through various channels (push
    notifications, SMS, webhooks, etc.).
    """

    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        channel: str = "push",
        metadata: dict[str, any] | None = None,
    ) -> None:
        """Send a notification to a user.

        Args:
            user_id: User identifier
            title: Notification title
            message: Notification message
            channel: Notification channel (push, sms, email, webhook)
            metadata: Additional metadata (optional)

        Raises:
            NotificationSendError: If sending fails
        """
        ...

    async def send_batch(
        self,
        notifications: list[dict[str, any]],
    ) -> None:
        """Send multiple notifications.

        Args:
            notifications: List of notification dictionaries

        Raises:
            NotificationSendError: If sending fails
        """
        ...

    async def get_notification_status(
        self,
        _notification_id: str,
    ) -> dict[str, any]:
        """Get notification delivery status.

        Args:
            notification_id: Notification identifier

        Returns:
            Notification status dictionary

        Raises:
            NotificationNotFoundError: If notification doesn't exist
        """
        ...


class MetricsService(Protocol):
    """Metrics service protocol.

    Defines the contract for recording and querying metrics. Adapters can implement this
    for different metrics backends (Prometheus, StatsD, CloudWatch, etc.).
    """

    async def record_counter(
        self,
        name: str,
        value: float = 1.0,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a counter metric.

        Args:
            name: Metric name
            value: Counter value (default: 1.0)
            tags: Metric tags (optional)
        """
        ...

    async def record_gauge(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            tags: Metric tags (optional)
        """
        ...

    async def record_histogram(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a histogram metric.

        Args:
            name: Metric name
            value: Histogram value
            tags: Metric tags (optional)
        """
        ...

    async def record_timing(
        self,
        name: str,
        duration_ms: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a timing metric.

        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Metric tags (optional)
        """
        ...

    async def query_metric(
        self,
        name: str,
        start_time: str | None = None,
        end_time: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> list[dict[str, any]]:
        """Query metric values.

        Args:
            name: Metric name
            start_time: Start time (ISO format, optional)
            end_time: End time (ISO format, optional)
            tags: Filter by tags (optional)

        Returns:
            List of metric data points
        """
        ...
