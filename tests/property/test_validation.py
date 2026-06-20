"""Property-based tests for model validation with random/adversarial inputs.

Validates that Pydantic models reject bad data gracefully (never crash with an
unhandled exception) and that validators enforce documented constraints.
"""

import string

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from tests.test_constants import COUNT_FOUR
from tracertm.schemas.account import AccountCreate
from tracertm.schemas.item import ItemCreate
from tracertm.schemas.link import LinkCreate
from tracertm.schemas.problem import ImpactLevel, ProblemCreate
from tracertm.schemas.test_case import TestStep as TStep
from tracertm.validation.id_validator import (
    is_valid_uuid,
    normalize_uuid,
)

# ---------------------------------------------------------------------------
# Strategies for adversarial inputs
# ---------------------------------------------------------------------------

arbitrary_text = st.text(max_size=2000)
arbitrary_bytes_as_str = st.binary(max_size=500).map(lambda b: b.decode("utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.property
class TestItemValidationNeverCrashes:
    """ItemCreate and ItemUpdate validation never raises unhandled exceptions."""

    @given(data=st.dictionaries(st.text(max_size=50), st.text(max_size=200), max_size=10))
    @settings(max_examples=100)
    def test_item_create_with_arbitrary_dict(self, data: dict) -> None:
        """Constructing ItemCreate from arbitrary dict either succeeds or raises ValidationError."""
        try:
            ItemCreate(**data)
        except (ValidationError, TypeError):
            pass  # Expected for bad data

    @given(
        title=arbitrary_text,
        view=arbitrary_text,
        item_type=arbitrary_text,
        status=arbitrary_text,
    )
    @settings(max_examples=100)
    def test_item_create_with_arbitrary_strings(self, title: str, view: str, item_type: str, status: str) -> None:
        """ItemCreate with arbitrary string fields never crashes unexpectedly."""
        try:
            ItemCreate(title=title, view=view, item_type=item_type, status=status)
        except (ValidationError, TypeError):
            pass

    @given(title=st.text(min_size=501, max_size=1000))
    @settings(max_examples=100)
    def test_item_create_title_max_length_enforced(self, title: str) -> None:
        """Titles exceeding 500 chars must be rejected."""
        with pytest.raises(ValidationError):
            ItemCreate(title=title, view="FEATURE", item_type="feature")

    @given(title=st.just(""))
    @settings(max_examples=5)
    def test_item_create_empty_title_rejected(self, title: str) -> None:
        """Empty title is rejected by min_length=1."""
        with pytest.raises(ValidationError):
            ItemCreate(title=title, view="FEATURE", item_type="feature")


@pytest.mark.property
class TestLinkValidationNeverCrashes:
    """LinkCreate validation never raises unhandled exceptions."""

    @given(data=st.dictionaries(st.text(max_size=50), st.text(max_size=200), max_size=10))
    @settings(max_examples=100)
    def test_link_create_with_arbitrary_dict(self, data: dict) -> None:
        """LinkCreate from arbitrary dict either succeeds or raises ValidationError."""
        try:
            LinkCreate(**data)
        except (ValidationError, TypeError):
            pass


@pytest.mark.property
class TestAccountValidation:
    """AccountCreate validation invariants."""

    @given(
        name=st.text(max_size=300),
        account_type=st.text(max_size=50),
    )
    @settings(max_examples=100)
    def test_account_create_arbitrary_inputs(self, name: str, account_type: str) -> None:
        """AccountCreate with arbitrary inputs never crashes -- rejects cleanly."""
        try:
            AccountCreate(name=name, account_type=account_type)
        except (ValidationError, TypeError):
            pass

    @given(name=st.text(min_size=1, max_size=255, alphabet=st.characters(whitelist_categories=("L", "N"))))
    @settings(max_examples=100)
    def test_account_create_valid_name_always_accepts(self, name: str) -> None:
        """A valid name with valid account_type always passes validation."""
        account = AccountCreate(name=name, account_type="personal")
        assert account.name == name
        assert account.account_type == "personal"

    @given(account_type=st.text(min_size=1, max_size=50).filter(lambda s: s not in {"personal", "organization"}))
    @settings(max_examples=100)
    def test_account_type_rejects_invalid_values(self, account_type: str) -> None:
        """Only 'personal' or 'organization' are accepted."""
        with pytest.raises(ValidationError):
            AccountCreate(name="test", account_type=account_type)


@pytest.mark.property
class TestProblemValidation:
    """ProblemCreate field validation."""

    @given(
        title=st.text(min_size=1, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        impact=st.sampled_from(list(ImpactLevel)),
    )
    @settings(max_examples=100)
    def test_problem_create_valid_always_succeeds(self, title: str, impact: ImpactLevel) -> None:
        """ProblemCreate with valid inputs always succeeds."""
        problem = ProblemCreate(title=title, impact_level=impact)
        assert problem.title == title
        assert problem.impact_level == impact


@pytest.mark.property
class TestUUIDValidator:
    """Property-based tests for UUID validation utility."""

    @given(uuid_str=st.uuids().map(str))
    @settings(max_examples=100)
    def test_valid_uuid_always_passes(self, uuid_str: str) -> None:
        """Any UUID generated by uuid4 must pass validation."""
        assert is_valid_uuid(uuid_str)

    @given(uuid_str=st.uuids().map(str))
    @settings(max_examples=100)
    def test_normalize_is_idempotent(self, uuid_str: str) -> None:
        """Normalizing a UUID twice yields the same result."""
        once = normalize_uuid(uuid_str)
        twice = normalize_uuid(once)
        assert once == twice

    @given(uuid_str=st.uuids().map(lambda u: str(u).upper()))
    @settings(max_examples=100)
    def test_uppercase_uuid_normalizes_to_lowercase(self, uuid_str: str) -> None:
        """Uppercase UUIDs normalize to lowercase and pass validation."""
        normalized = normalize_uuid(uuid_str)
        assert normalized == uuid_str.lower()
        assert is_valid_uuid(normalized)

    @given(text=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_random_text_not_valid_uuid(self, text: str) -> None:
        """Random alphanumeric strings that aren't UUIDs should fail validation."""
        # Filter out strings that happen to be valid UUIDs
        assume(len(text) != 36 or text.count("-") != COUNT_FOUR)
        assert not is_valid_uuid(text)

    @given(uuid_str=st.uuids().map(str), padding=st.sampled_from(["", " ", "  ", "\t", "\n"]))
    @settings(max_examples=100)
    def test_whitespace_padding_handled(self, uuid_str: str, padding: str) -> None:
        """UUID with whitespace padding is normalized correctly."""
        padded = padding + uuid_str + padding
        normalized = normalize_uuid(padded)
        assert normalized == uuid_str.lower().strip()


@pytest.mark.property
class TestTestStepValidation:
    """TestStep field constraints."""

    @given(step_number=st.integers(max_value=0))
    @settings(max_examples=50)
    def test_step_number_must_be_positive(self, step_number: int) -> None:
        """step_number < 1 is rejected."""
        with pytest.raises(ValidationError):
            TStep(step_number=step_number, action="do something")

    @given(step_number=st.integers(min_value=1, max_value=10000))
    @settings(max_examples=100)
    def test_valid_step_number_accepted(self, step_number: int) -> None:
        """Positive step_number is accepted."""
        step = TStep(step_number=step_number, action="do something")
        assert step.step_number == step_number
