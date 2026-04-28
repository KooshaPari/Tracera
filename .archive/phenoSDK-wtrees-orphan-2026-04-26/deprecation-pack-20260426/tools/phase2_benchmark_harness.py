"""Phase 2 benchmark harness for SDK analytics and secret scanning.

This script orchestrates benchmark runs for the pheno-sdk analytics and
secret scanning pipelines across Morph and Router repositories. It does not
execute heavy benchmarks automatically; instead, it prepares configuration, 
documents required environment variables, and provides helper commands to run
on developer or CI workstations with appropriate resources.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict, dataclass

ROOT = pathlib.Path(__file__).resolve().parents[2]
MORPH_ROOT = ROOT / "morph"
SDK_ROOT = ROOT / "pheno-sdk"


@dataclass
class BenchmarkConfig:
    repo_path: str
    benchmark_module: str
    dataset_dir: str
    output_dir: str
    warmup_runs: int = 1
    benchmark_runs: int = 3


DEFAULT_CONFIGS: dict[str, BenchmarkConfig] = {
    "analytics": BenchmarkConfig(
        repo_path=str(SDK_ROOT),
        benchmark_module="pheno_sdk_benchmarks.analytics",
        dataset_dir=str(MORPH_ROOT / "tests" / "fixtures" / "repos"),
        output_dir=str(ROOT / "benchmark_results" / "analytics"),
    ),
    "secret_scan": BenchmarkConfig(
        repo_path=str(SDK_ROOT),
        benchmark_module="pheno_sdk_benchmarks.secret_scan",
        dataset_dir=str(MORPH_ROOT / "tests" / "fixtures" / "repos"),
        output_dir=str(ROOT / "benchmark_results" / "secret_scan"),
    ),
}


def dump_config(name: str, config: BenchmarkConfig) -> None:
    print(json.dumps({name: asdict(config)}, indent=2))


def run_benchmark(config: BenchmarkConfig, extra_args: list[str]) -> None:
    """Invoke the configured benchmark module in a subprocess.

    The benchmark modules are expected to live inside `sdk_root/tests/benchmarks`
    (to be implemented during Phase 2). Each module should expose a CLI entry
    point accepting the dataset and output directories.
    """

    cmd = [
        sys.executable,
        "-m",
        config.benchmark_module,
        "--dataset",
        config.dataset_dir,
        "--output",
        config.output_dir,
        "--warmup-runs",
        str(config.warmup_runs),
        "--benchmark-runs",
        str(config.benchmark_runs),
        *extra_args,
    ]

    print("Running benchmark:", " ".join(cmd))
    subprocess.run(cmd, cwd=config.repo_path, check=True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Phase 2 benchmark harness")
    parser.add_argument(
        "target",
        choices=sorted(DEFAULT_CONFIGS.keys()),
        help="Benchmark target (analytics or secret_scan)",
    )
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Additional args")
    parser.add_argument("--dry-run", action="store_true", help="Print configuration only")

    args = parser.parse_args(argv)
    config = DEFAULT_CONFIGS[args.target]

    if args.dry_run:
        dump_config(args.target, config)
        return 0

    try:
        run_benchmark(config, args.extra)
    except subprocess.CalledProcessError as exc:
        print(f"Benchmark failed (exit code {exc.returncode})", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
