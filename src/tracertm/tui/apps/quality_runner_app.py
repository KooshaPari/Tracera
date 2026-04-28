"""Quality runner TUI application.

Rich dashboard for DAG-based quality runs with live logs and action plan.
"""

from typing import Any, ClassVar

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Footer, Header, Static

    from tracertm.tui.quality_root import ROOT
    from tracertm.tui.widgets.action_plan_panel import ActionPlanPanel
    from tracertm.tui.widgets.agent_process_list import AgentProcessList
    from tracertm.tui.widgets.live_log_view import LiveLogView
    from tracertm.tui.widgets.step_status_table import StepStatusTable

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:

    class QualityRunnerApp(App):
        """Quality runner TUI with step status, live logs, and action plan."""

        CSS = """
        Screen {
            background: $surface;
        }

        #steps-panel {
            width: 35%;
            border-right: wide $primary;
            height: 1fr;
        }

        #log-panel {
            width: 65%;
            height: 1fr;
        }

        #agents-panel {
            height: auto;
            max-height: 20%;
            border-top: solid $primary;
        }

        #action-panel {
            height: 1fr;
            border-top: solid $primary;
        }

        StepStatusTable {
            height: 1fr;
        }

        LiveLogView {
            height: 1fr;
        }
        """

        BINDINGS: ClassVar[list[Binding]] = [
            Binding("q", "quit", "Quit", priority=True),
            Binding("r", "refresh", "Refresh"),
            Binding("R", "run_quality", "Run quality DAG"),
            Binding("f", "fix", "Run fix agents"),
        ]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)

            with Horizontal():
                with Vertical(id="steps-panel"):
                    yield Static("Steps (DAG)", id="steps-title")
                    yield StepStatusTable(id="step-table")

                with Vertical(id="log-panel"):
                    yield Static("Live Log (select step)", id="log-title")
                    yield LiveLogView(id="live-log")

            with Container(id="agents-panel"):
                yield Static("Fix Agents", id="agents-title")
                yield AgentProcessList(id="agent-list")

            with Container(id="action-panel"):
                yield Static("Action Plan (by file)", id="action-title")
                yield ActionPlanPanel(id="action-plan")

            yield Footer()

        def on_mount(self) -> None:
            self.refresh_all()
            self.set_interval(2.0, self.refresh_all)
            self._select_first_step()

        def _select_first_step(self) -> None:
            step_table = self.query_one("#step-table", StepStatusTable)
            if step_table.row_count > 0:
                step_table.cursor_row = 0
                self._on_step_selected()

        def refresh_all(self) -> None:
            """Refresh all panels."""
            step_table = self.query_one("#step-table", StepStatusTable)
            step_table.refresh_steps()

            log_view = self.query_one("#live-log", LiveLogView)
            log_view.refresh_log()

            agent_list = self.query_one("#agent-list", AgentProcessList)
            agent_list.refresh_content()

            action_plan = self.query_one("#action-plan", ActionPlanPanel)
            action_plan.refresh_content()

        def _on_step_selected(self) -> None:
            step_table = self.query_one("#step-table", StepStatusTable)
            step_name = step_table.get_selected_step()
            if step_name:
                log_view = self.query_one("#live-log", LiveLogView)
                log_view.show_step(step_name)

        def on_data_table_row_selected(self, event: Any) -> None:
            self._on_step_selected()

        def action_refresh(self) -> None:
            self.refresh_all()
            self.notify("Refreshed", severity="information")

        def action_run_quality(self) -> None:
            """Run quality DAG in background."""
            self.run_worker(self._run_quality_worker, thread=True)

        def _run_quality_worker(self) -> None:
            """Worker that runs quality DAG with TUI progress via task."""
            import subprocess

            proc = subprocess.run(
                ["task", "quality:dag:tui"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.call_from_thread(self.refresh_all)
            if proc.returncode == 0:
                self.call_from_thread(self.notify, "Quality passed", severity="information")
            else:
                self.call_from_thread(self.notify, "Quality failed", severity="error")

        def action_fix(self) -> None:
            """Run fix agents for failed steps."""
            self.run_worker(self._run_fix_worker, thread=True)

        def _run_fix_worker(self) -> None:
            """Worker that runs fix agents via task."""
            import subprocess

            proc = subprocess.run(
                ["task", "quality:fix"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.call_from_thread(self.refresh_all)
            if proc.returncode == 0:
                self.call_from_thread(self.notify, "Fix agents completed", severity="information")
            else:
                self.call_from_thread(self.notify, "Some fix agents failed", severity="warning")
