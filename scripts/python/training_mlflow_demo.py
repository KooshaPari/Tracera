"""Example training loop wired to TraceRTM's MLflow-compatible tracking."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tracertm.mlflow_compat import TrackingClient


def main() -> None:
    """Run a tiny demo loop and log MLflow-compatible training telemetry."""
    client = TrackingClient()
    run = client.start_run()
    run.log_params({"model": "linear-demo", "epochs": 3, "optimizer": "sgd"})

    with tempfile.TemporaryDirectory() as temp_dir:
        artifact_dir = Path(temp_dir)
        for step in range(3):
            run.log_metric("loss", 1.0 / (step + 1), step=step)
            run.log_metric("accuracy", 0.72 + (step * 0.08), step=step)
            run.log_metric("lr", 0.01 / (step + 1), step=step)

        config = artifact_dir / "config.json"
        model = artifact_dir / "model.json"
        plot = artifact_dir / "loss_plot.txt"
        config.write_text(json.dumps({"batch_size": 16, "seed": 7}), encoding="utf-8")
        model.write_text(json.dumps({"weights": [0.2, 0.8]}), encoding="utf-8")
        plot.write_text("loss: 1.0 -> 0.5 -> 0.333\n", encoding="utf-8")

        run.log_artifact(model)
        run.log_artifact(plot)
        run.log_artifact(config)

    run.end()


if __name__ == "__main__":
    main()
