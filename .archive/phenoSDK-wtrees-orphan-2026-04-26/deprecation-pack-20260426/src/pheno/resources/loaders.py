"""Resource data loaders and managers.

Handles loading resource budgets, allocations, and related data from various sources
with validation and conversion.
"""

import json
import logging
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from pheno.resources.budget import (
    AllocationStrategy,
    BudgetPeriod,
    ResourceAllocation,
    ResourceBudget,
)
from pheno.resources.trackers import HistoricalAnalyzer, PredictivePlanner, UsageTracker

logger = logging.getLogger(__name__)


class BudgetLoader:
    """
    Loads and validates resource budgets from configuration.
    """

    def __init__(self):
        self._validators = {
            BudgetPeriod.HOURLY: self._validate_hourly_budget,
            BudgetPeriod.DAILY: self._validate_daily_budget,
            BudgetPeriod.WEEKLY: self._validate_weekly_budget,
            BudgetPeriod.MONTHLY: self._validate_monthly_budget,
        }

    def load_from_file(self, file_path: str | Path) -> list[ResourceBudget]:
        """Load budgets from configuration file.

        Supports JSON, YAML, and TOML formats.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Budget configuration file not found: {file_path}")

        # Load configuration based on file extension
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            config = self._load_json(file_path)
        elif suffix in [".yml", ".yaml"]:
            config = self._load_yaml(file_path)
        elif suffix == ".toml":
            config = self._load_toml(file_path)
        else:
            raise ValueError(f"Unsupported configuration format: {suffix}")

        return self.load_from_config(config)

    def load_from_config(self, config: dict[str, Any]) -> list[ResourceBudget]:
        """
        Load budgets from configuration dictionary.
        """
        budgets = []

        budget_configs = config.get("budgets", [])

        for budget_config in budget_configs:
            try:
                budget = self._create_budget_from_config(budget_config)
                budgets.append(budget)
            except Exception as e:
                logger.exception(f"Failed to create budget from config: {budget_config}, error: {e}")
                continue

        return budgets

    def _create_budget_from_config(self, config: dict[str, Any]) -> ResourceBudget:
        """
        Create ResourceBudget from configuration.
        """
        # Required fields
        resource_type = config["resource_type"]
        period_str = config["period"]
        total_units = float(config["total_units"])

        # Convert period string to enum
        try:
            period = BudgetPeriod(period_str.lower())
        except ValueError:
            raise ValueError(f"Invalid budget period: {period_str}")

        # Optional fields
        total_budget_usd = config.get("total_budget_usd")
        if total_budget_usd is not None:
            total_budget_usd = float(total_budget_usd)

        metadata = config.get("metadata", {})

        # Calculate period end
        now = datetime.now(UTC)
        period_end = self._calculate_period_end(now, period)

        # Validate budget
        self._validate_budget(total_units, total_budget_usd, period)

        return ResourceBudget(
            resource_type=resource_type,
            period=period,
            total_units=total_units,
            total_budget_usd=total_budget_usd,
            period_start=now,
            period_end=period_end,
            metadata=metadata,
        )

    def _calculate_period_end(self, start: datetime, period: BudgetPeriod) -> datetime:
        """
        Calculate period end time based on period type.
        """
        if period == BudgetPeriod.HOURLY:
            return start + timedelta(hours=1)
        if period == BudgetPeriod.DAILY:
            return start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        if period == BudgetPeriod.WEEKLY:
            return start + timedelta(days=7 - start.weekday())
        if period == BudgetPeriod.MONTHLY:
            next_month = start.month + 1 if start.month < 12 else 1
            next_year = start.year if start.month < 12 else start.year + 1
            return start.replace(
                year=next_year, month=next_month, day=1, hour=0, minute=0, second=0, microsecond=0,
            ) - timedelta(seconds=1)
        raise ValueError(f"Unsupported period: {period}")

    def _validate_budget(
        self, total_units: float, total_budget_usd: float | None, period: BudgetPeriod,
    ) -> None:
        """
        Validate budget parameters.
        """
        if total_units <= 0:
            raise ValueError("Total units must be positive")

        if total_budget_usd is not None and total_budget_usd <= 0:
            raise ValueError("Total budget USD must be positive if specified")

        # Period-specific validation
        validator = self._validators.get(period)
        if validator:
            validator(total_units, total_budget_usd)

    def _validate_hourly_budget(
        self, total_units: float, total_budget_usd: float | None,
    ) -> None:
        """
        Validate hourly budget constraints.
        """
        # Add hourly-specific validation logic
        if total_units > 1000000:  # Example threshold
            logger.warning(f"Hourly budget very large: {total_units} units")

    def _validate_daily_budget(self, total_units: float, total_budget_usd: float | None) -> None:
        """
        Validate daily budget constraints.
        """
        if total_units > 10000000:  # Example threshold
            logger.warning(f"Daily budget very large: {total_units} units")

    def _validate_weekly_budget(
        self, total_units: float, total_budget_usd: float | None,
    ) -> None:
        """
        Validate weekly budget constraints.
        """
        if total_units > 50000000:  # Example threshold
            logger.warning(f"Weekly budget very large: {total_units} units")

    def _validate_monthly_budget(
        self, total_units: float, total_budget_usd: float | None,
    ) -> None:
        """
        Validate monthly budget constraints.
        """
        if total_units > 200000000:  # Example threshold
            logger.warning(f"Monthly budget very large: {total_units} units")

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        """
        Load JSON configuration file.
        """
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """
        Load YAML configuration file.
        """
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_toml(self, file_path: Path) -> dict[str, Any]:
        """
        Load TOML configuration file.
        """
        with open(file_path, "rb") as f:
            return tomllib.load(f)


class AllocationLoader:
    """
    Loads and manages resource allocations with validation.
    """

    def __init__(self):
        self.usage_tracker = UsageTracker()
        self.historical_analyzer = HistoricalAnalyzer(self.usage_tracker)
        self.predictive_planner = PredictivePlanner(self.historical_analyzer)

    def create_allocation(
        self,
        request_id: str,
        resource_type: str,
        requested_units: float,
        allocated_units: float,
        strategy: AllocationStrategy,
        estimated_cost_usd: float = 0.0,
        model_name: str | None = None,
        operation_type: str | None = None,
        priority: int = 5,
        metadata: dict[str, Any] | None = None,
    ) -> ResourceAllocation:
        """
        Create a new resource allocation with validation.
        """
        # Validate parameters
        self._validate_allocation_params(
            request_id=request_id,
            resource_type=resource_type,
            requested_units=requested_units,
            allocated_units=allocated_units,
            estimated_cost_usd=estimated_cost_usd,
            priority=priority,
        )

        # Generate allocation ID
        allocation_id = f"{request_id}_{datetime.now(UTC).timestamp()}"

        # Create allocation
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            request_id=request_id,
            resource_type=resource_type,
            model_name=model_name,
            operation_type=operation_type,
            requested_units=requested_units,
            allocated_units=allocated_units,
            estimated_cost_usd=estimated_cost_usd,
            priority=priority,
            strategy=strategy,
            metadata=metadata or {},
        )

        logger.debug(
            f"Created allocation {allocation_id}: {allocated_units} units of {resource_type}",
        )

        return allocation

    def _validate_allocation_params(
        self,
        request_id: str,
        resource_type: str,
        requested_units: float,
        allocated_units: float,
        estimated_cost_usd: float,
        priority: int,
    ) -> None:
        """
        Validate allocation parameters.
        """
        if not request_id:
            raise ValueError("Request ID is required")

        if not resource_type:
            raise ValueError("Resource type is required")

        if requested_units <= 0:
            raise ValueError("Requested units must be positive")

        if allocated_units <= 0:
            raise ValueError("Allocated units must be positive")

        if allocated_units > requested_units:
            raise ValueError("Allocated units cannot exceed requested units")

        if estimated_cost_usd < 0:
            raise ValueError("Estimated cost cannot be negative")

        if not (1 <= priority <= 10):
            raise ValueError("Priority must be between 1 and 10")

    def load_from_history(self, history_data: list[dict[str, Any]]) -> list[ResourceAllocation]:
        """
        Load allocations from history data.
        """
        allocations = []

        for item in history_data:
            try:
                allocation = self._create_allocation_from_history(item)
                allocations.append(allocation)
            except Exception as e:
                logger.exception(f"Failed to load allocation from history: {item}, error: {e}")
                continue

        return allocations

    def _create_allocation_from_history(self, data: dict[str, Any]) -> ResourceAllocation:
        """
        Create ResourceAllocation from history data.
        """
        # Convert string dates to datetime objects
        created_at = self._parse_datetime(data.get("created_at"))
        completed_at = self._parse_datetime(data.get("completed_at"))

        # Convert strategy string to enum
        strategy_str = data.get("strategy", "dynamic")
        try:
            strategy = AllocationStrategy(strategy_str.lower())
        except ValueError:
            strategy = AllocationStrategy.DYNAMIC

        allocation = ResourceAllocation(
            allocation_id=data["allocation_id"],
            request_id=data["request_id"],
            resource_type=data["resource_type"],
            model_name=data.get("model_name"),
            operation_type=data.get("operation_type"),
            requested_units=float(data["requested_units"]),
            allocated_units=float(data["allocated_units"]),
            used_units=float(data.get("used_units", 0.0)),
            estimated_cost_usd=float(data.get("estimated_cost_usd", 0.0)),
            actual_cost_usd=float(data.get("actual_cost_usd", 0.0)),
            priority=int(data.get("priority", 5)),
            strategy=strategy,
            is_active=data.get("is_active", False),
            is_completed=data.get("is_completed", False),
            exceeded_allocation=data.get("exceeded_allocation", False),
            metadata=data.get("metadata", {}),
        )

        allocation.created_at = created_at
        allocation.completed_at = completed_at

        return allocation

    def _parse_datetime(self, dt_str: str | None) -> datetime | None:
        """
        Parse datetime string to datetime object.
        """
        if not dt_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Try timestamp format
                return datetime.fromtimestamp(float(dt_str), tz=UTC)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse datetime: {dt_str}")
                return None


class ResourceLimitsLoader:
    """
    Loads and manages resource limits and constraints.
    """

    def load_limits_from_config(self, config_file: str | Path) -> dict[str, dict[str, Any]]:
        """
        Load resource limits from configuration file.
        """
        config_file = Path(config_file)

        if not config_file.exists():
            raise FileNotFoundError(f"Limits configuration file not found: {config_file}")

        # Load configuration based on file type
        if config_file.suffix.lower() == ".json":
            config = self._load_json(config_file)
        elif config_file.suffix.lower() in [".yml", ".yaml"]:
            config = self._load_yaml(config_file)
        else:
            raise ValueError(f"Unsupported config format: {config_file.suffix}")

        return self._parse_limits_config(config)

    def _parse_limits_config(self, config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """
        Parse limits configuration dictionary.
        """
        limits = {}

        limits_config = config.get("resource_limits", {})

        for identifier, limit_config in limits_config.items():
            try:
                limits[identifier] = self._parse_single_limit(limit_config)
            except Exception as e:
                logger.exception(f"Failed to parse limit for {identifier}: {e}")
                continue

        return limits

    def _parse_single_limit(self, limit_config: dict[str, Any]) -> dict[str, Any]:
        """
        Parse a single limit configuration.
        """
        limits = {}

        # Required max_units
        if "max_units" not in limit_config:
            raise ValueError("max_units is required in limit configuration")

        limits["max_units"] = float(limit_config["max_units"])

        # Optional limits
        optional_fields = [
            "max_cost_usd",
            "requests_per_minute",
            "concurrent_requests",
            "cooldown_period",
            "retry_limit",
        ]

        for field in optional_fields:
            if field in limit_config:
                if field in ["requests_per_minute", "concurrent_requests", "retry_limit"]:
                    limits[field] = int(limit_config[field])
                elif field == "cooldown_period":
                    limits[field] = int(limit_config[field])  # seconds
                else:
                    limits[field] = float(limit_config[field])

        # Optional metadata
        if "metadata" in limit_config:
            limits["metadata"] = limit_config["metadata"]

        return limits

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        """
        Load JSON configuration.
        """
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """
        Load YAML configuration.
        """
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
