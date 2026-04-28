"""
Security policy management.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.security.sandbox.policy")


class PolicyAction(Enum):
    """
    Policy actions.
    """

    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"


@dataclass(slots=True)
class PolicyRule:
    """
    Security policy rule.
    """

    name: str
    pattern: str
    action: PolicyAction
    description: str = ""
    conditions: dict[str, Any] = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}


class PolicyViolationError(Exception):
    """
    Raised when policy is violated.
    """



class SecurityPolicy:
    """
    Security policy implementation.
    """

    def __init__(self):
        self.rules: list[PolicyRule] = []
        self._rule_cache: dict[str, PolicyRule] = {}

    def add_rule(self, rule: PolicyRule) -> None:
        """
        Add policy rule.
        """
        self.rules.append(rule)
        self._rule_cache[rule.name] = rule
        logger.debug(f"Added policy rule: {rule.name}")

    def remove_rule(self, name: str) -> bool:
        """
        Remove policy rule.
        """
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                del self.rules[i]
                if name in self._rule_cache:
                    del self._rule_cache[name]
                logger.debug(f"Removed policy rule: {name}")
                return True
        return False

    def check_policy(self, resource: str, action: str) -> PolicyAction:
        """
        Check policy for resource and action.
        """
        for rule in self.rules:
            if self._matches_rule(resource, action, rule):
                return rule.action
        return PolicyAction.ALLOW  # Default allow

    def _matches_rule(self, resource: str, action: str, rule: PolicyRule) -> bool:
        """
        Check if resource matches rule pattern.
        """
        # Simple pattern matching - can be enhanced with regex
        return rule.pattern in resource


class PolicyManager:
    """
    Manages multiple security policies.
    """

    def __init__(self):
        self.policies: dict[str, SecurityPolicy] = {}
        self.default_policy = SecurityPolicy()

    def create_policy(self, name: str) -> SecurityPolicy:
        """
        Create new policy.
        """
        policy = SecurityPolicy()
        self.policies[name] = policy
        logger.info(f"Created policy: {name}")
        return policy

    def get_policy(self, name: str) -> SecurityPolicy | None:
        """
        Get policy by name.
        """
        return self.policies.get(name)

    def remove_policy(self, name: str) -> bool:
        """
        Remove policy.
        """
        if name in self.policies:
            del self.policies[name]
            logger.info(f"Removed policy: {name}")
            return True
        return False
