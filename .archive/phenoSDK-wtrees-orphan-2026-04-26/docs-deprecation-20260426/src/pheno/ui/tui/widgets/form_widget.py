"""
FormWidget - Interactive form builder with validation.

Provides dynamic form creation with:
- Multiple field types
- Validation rules
- Submit/cancel handlers
- Field dependencies
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from rich.panel import Panel
    from textual import on
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.reactive import reactive
    from textual.widgets import Button, Checkbox, Input, Label, Select, Static

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Static = object
    Input = object

    class Button:
        class Pressed:
            pass

    Checkbox = object
    Select = object
    Label = object
    Container = object
    Horizontal = object
    Vertical = object
    def reactive(x):
        return x
    ComposeResult = object
    Panel = object
    def on(*args, **kwargs):
        return lambda f: f


class FieldType(Enum):
    """
    Form field types.
    """

    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    EMAIL = "email"
    CHECKBOX = "checkbox"
    SELECT = "select"
    TEXTAREA = "textarea"


@dataclass
class FormField:
    """
    Form field definition.
    """

    name: str
    label: str
    field_type: FieldType
    required: bool = False
    default_value: Any = None
    placeholder: str = ""
    options: list[tuple] = field(default_factory=list)  # For select fields
    validator: Callable[[Any], bool] | None = None
    error_message: str = "Invalid value"
    help_text: str = ""

    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validate field value.
        """
        # Required check
        if self.required and not value:
            return False, f"{self.label} is required"

        # Custom validator
        if self.validator and value:
            try:
                if not self.validator(value):
                    return False, self.error_message
            except Exception as e:
                return False, str(e)

        # Type-specific validation
        if self.field_type == FieldType.EMAIL and value:
            if "@" not in value or "." not in value.split("@")[-1]:
                return False, "Invalid email address"

        if self.field_type == FieldType.NUMBER and value:
            try:
                float(value)
            except ValueError:
                return False, "Must be a number"

        return True, ""


class FormWidget(Static):
    """Dynamic form widget with validation.

    Features:
    - Multiple field types
    - Built-in and custom validation
    - Submit/cancel handlers
    - Field state management
    - Error display
    """

    is_valid = reactive(False)
    is_submitted = reactive(False)

    def __init__(
        self,
        fields: list[FormField],
        submit_label: str = "Submit",
        cancel_label: str = "Cancel",
        show_cancel: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.fields = fields
        self.submit_label = submit_label
        self.cancel_label = cancel_label
        self.show_cancel = show_cancel
        self._field_widgets: dict[str, Any] = {}
        self._field_errors: dict[str, str] = {}
        self._submit_callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._cancel_callbacks: list[Callable[[], None]] = []

    def compose(self) -> ComposeResult:
        """
        Create form layout.
        """
        with Container(id="form-container"):
            # Form title
            yield Label("[bold]Form[/bold]", id="form-title")

            # Field container
            with Vertical(id="fields-container"):
                for field_def in self.fields:
                    with Container(classes="field-group"):
                        # Field label
                        label_text = field_def.label
                        if field_def.required:
                            label_text += " *"

                        yield Label(label_text, classes="field-label")

                        # Field widget based on type
                        field_widget = self._create_field_widget(field_def)
                        yield field_widget

                        # Help text
                        if field_def.help_text:
                            yield Label(f"[dim]{field_def.help_text}[/dim]", classes="field-help")

                        # Error message placeholder
                        yield Label("", classes="field-error", id=f"error-{field_def.name}")

            # Buttons
            with Horizontal(id="form-buttons"):
                yield Button(self.submit_label, variant="primary", id="submit-btn")
                if self.show_cancel:
                    yield Button(self.cancel_label, id="cancel-btn")

    def _create_field_widget(self, field_def: FormField) -> Any:
        """
        Create appropriate widget for field type.
        """
        widget_id = f"field-{field_def.name}"

        if field_def.field_type == FieldType.CHECKBOX:
            widget = Checkbox(field_def.label, value=field_def.default_value or False, id=widget_id)

        elif field_def.field_type == FieldType.SELECT:
            widget = Select(options=field_def.options, value=field_def.default_value, id=widget_id)

        elif field_def.field_type == FieldType.PASSWORD:
            widget = Input(
                placeholder=field_def.placeholder,
                password=True,
                value=str(field_def.default_value or ""),
                id=widget_id,
            )

        else:  # TEXT, EMAIL, NUMBER, TEXTAREA
            widget = Input(
                placeholder=field_def.placeholder,
                value=str(field_def.default_value or ""),
                id=widget_id,
            )

        self._field_widgets[field_def.name] = widget
        return widget

    @on(Button.Pressed, "#submit-btn")
    def handle_submit(self) -> None:
        """
        Handle form submission.
        """
        # Validate all fields
        self._field_errors.clear()
        values = {}

        for field_def in self.fields:
            widget_id = f"field-{field_def.name}"

            try:
                widget = self.query_one(f"#{widget_id}")

                # Get value based on widget type
                if isinstance(widget, (Checkbox, Select, Input)):
                    value = widget.value
                else:
                    value = None

                # Validate
                is_valid, error_msg = field_def.validate(value)

                if not is_valid:
                    self._field_errors[field_def.name] = error_msg
                    # Show error
                    error_label = self.query_one(f"#error-{field_def.name}", Label)
                    error_label.update(f"[red]{error_msg}[/red]")
                else:
                    # Clear error
                    error_label = self.query_one(f"#error-{field_def.name}", Label)
                    error_label.update("")
                    values[field_def.name] = value

            except Exception as e:
                self._field_errors[field_def.name] = str(e)

        # Check if form is valid
        if not self._field_errors:
            self.is_valid = True
            self.is_submitted = True

            # Call submit callbacks
            for callback in self._submit_callbacks:
                try:
                    callback(values)
                except Exception as e:
                    print(f"Submit callback error: {e}")
        else:
            self.is_valid = False

    @on(Button.Pressed, "#cancel-btn")
    def handle_cancel(self) -> None:
        """
        Handle form cancellation.
        """
        # Call cancel callbacks
        for callback in self._cancel_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Cancel callback error: {e}")

    def get_values(self) -> dict[str, Any]:
        """
        Get current form values.
        """
        values = {}

        for field_def in self.fields:
            widget_id = f"field-{field_def.name}"

            try:
                widget = self.query_one(f"#{widget_id}")

                if isinstance(widget, (Checkbox, Select, Input)):
                    values[field_def.name] = widget.value

            except Exception:
                values[field_def.name] = None

        return values

    def set_values(self, values: dict[str, Any]) -> None:
        """
        Set form values.
        """
        for field_name, value in values.items():
            widget_id = f"field-{field_name}"

            try:
                widget = self.query_one(f"#{widget_id}")

                if isinstance(widget, Checkbox):
                    widget.value = bool(value)
                elif isinstance(widget, Select):
                    widget.value = value
                elif isinstance(widget, Input):
                    widget.value = str(value)

            except Exception as e:
                print(f"Error setting field {field_name}: {e}")

    def reset(self) -> None:
        """
        Reset form to default values.
        """
        for field_def in self.fields:
            widget_id = f"field-{field_def.name}"

            try:
                widget = self.query_one(f"#{widget_id}")

                if isinstance(widget, Checkbox):
                    widget.value = field_def.default_value or False
                elif isinstance(widget, Select):
                    widget.value = field_def.default_value
                elif isinstance(widget, Input):
                    widget.value = str(field_def.default_value or "")

                # Clear errors
                error_label = self.query_one(f"#error-{field_def.name}", Label)
                error_label.update("")

            except Exception:
                pass

        self._field_errors.clear()
        self.is_valid = False
        self.is_submitted = False

    def add_submit_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """
        Add callback for form submission.
        """
        self._submit_callbacks.append(callback)

    def add_cancel_callback(self, callback: Callable[[], None]) -> None:
        """
        Add callback for form cancellation.
        """
        self._cancel_callbacks.append(callback)

    def get_errors(self) -> dict[str, str]:
        """
        Get current validation errors.
        """
        return self._field_errors.copy()
