"""Test Template - Use this as a template for all new tests.

This template demonstrates the proper structure, naming, and documentation
for tests in the TraceRTM project.
"""

from typing import Any, cast

import pytest

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_fixture() -> None:
    """Fixture: Sample Setup.

    Provides: Test data and setup
    Cleanup: Automatic teardown
    """
    # Setup
    return {"key": "value"}

    # Teardown


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestEpicXStoryY:
    """Test Suite: Epic X - Story Y.

    Epic: X (Epic Title)
    Story: X.Y (Story Title)
    FRs: FR-XXX, FR-YYY
    Type: Unit|Integration|E2E
    """

    # ========================================================================
    # POSITIVE TEST CASES
    # ========================================================================

    @pytest.mark.unit
    @pytest.mark.critical
    def test_tc_X_Y_1_successful_operation(self, sample_fixture: Any) -> None:
        """TC-X.Y.1: Story Title - Successful Operation.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P0

        Given: Precondition is met
        When: Action is performed
        Then: Expected result occurs
        And: Side effect is correct
        """
        # Arrange
        data = sample_fixture

        # Act
        result = data["key"]

        # Assert
        assert result == "value"

    @pytest.mark.unit
    def test_tc_X_Y_2_alternative_scenario(self, sample_fixture: Any) -> None:
        """TC-X.Y.2: Story Title - Alternative Scenario.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P1

        Given: Different precondition
        When: Alternative action
        Then: Alternative result
        """
        # Arrange
        data = sample_fixture
        data["key"] = "new_value"

        # Act
        result = data["key"]

        # Assert
        assert result == "new_value"

    # ========================================================================
    # NEGATIVE TEST CASES
    # ========================================================================

    @pytest.mark.unit
    def test_tc_X_Y_3_error_handling(self, _sample_fixture: Any) -> None:
        """TC-X.Y.3: Story Title - Error Handling.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P1

        Given: Invalid input provided
        When: Operation attempted
        Then: Error is raised
        And: Error message is helpful
        """
        # Arrange
        data = None

        # Act & Assert (intentionally subscript None to raise TypeError)
        with pytest.raises(TypeError):
            _ = cast("Any", data)["key"]  # runtime: data is None -> TypeError

    # ========================================================================
    # EDGE CASE TEST CASES
    # ========================================================================

    @pytest.mark.unit
    def test_tc_X_Y_4_edge_case_empty_input(self) -> None:
        """TC-X.Y.4: Story Title - Edge Case Empty Input.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P2

        Given: Empty input provided
        When: Operation attempted
        Then: Graceful handling occurs
        """
        # Arrange
        data = {}

        # Act
        result = data.get("key", "default")

        # Assert
        assert result == "default"

    @pytest.mark.unit
    def test_tc_X_Y_5_edge_case_boundary_value(self) -> None:
        """TC-X.Y.5: Story Title - Edge Case Boundary Value.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P2

        Given: Boundary value provided
        When: Operation attempted
        Then: Correct handling occurs
        """
        # Arrange
        value = 0

        # Act
        result = value + 1

        # Assert
        assert result == 1


# ============================================================================
# INTEGRATION TEST CLASS
# ============================================================================


class TestEpicXStoryYIntegration:
    """Integration Test Suite: Epic X - Story Y.

    Tests interaction between multiple components
    """

    @pytest.mark.integration
    @pytest.mark.critical
    def test_tc_X_Y_6_component_interaction(self, sample_fixture: Any) -> None:
        """TC-X.Y.6: Story Title - Component Interaction.

        FR: FR-XXX
        Story: X.Y
        Type: Integration
        Priority: P0

        Given: Multiple components initialized
        When: Components interact
        Then: Integration works correctly
        """
        # Arrange
        data = sample_fixture

        # Act
        result = data["key"]

        # Assert
        assert result == "value"


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


class TestParametrized:
    """Parametrized Test Suite.

    Tests multiple scenarios with different inputs
    """

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("input_val", "expected"),
        [
            ("value1", "value1"),
            ("value2", "value2"),
            ("", ""),
        ],
    )
    def test_tc_X_Y_7_parametrized_scenarios(self, input_val: Any, expected: Any) -> None:
        """TC-X.Y.7: Story Title - Parametrized Scenarios.

        FR: FR-XXX
        Story: X.Y
        Type: Unit
        Priority: P1

        Tests multiple input scenarios
        """
        # Arrange
        data = {"key": input_val}

        # Act
        result = data["key"]

        # Assert
        assert result == expected


# ============================================================================
# NOTES
# ============================================================================

"""
GUIDELINES:

1. Test Naming:
   - Use TC-X.Y.Z-description format
   - Use test_tc_X_Y_Z_description function name
   - Use descriptive names

2. Test Structure:
   - Arrange: Setup test data
   - Act: Perform action
   - Assert: Verify results

3. Test Documentation:
   - Include FR reference
   - Include Story reference
   - Include Given/When/Then
   - Include Priority level

4. Test Organization:
   - Group by test class
   - Separate positive/negative/edge cases
   - Use markers for categorization

5. Test Independence:
   - Each test should be independent
   - Use fixtures for setup
   - Clean up after tests

6. Test Coverage:
   - Aim for 80%+ code coverage
   - Test happy path
   - Test error cases
   - Test edge cases
   - Test boundaries

7. Test Performance:
   - Keep unit tests fast (<100ms)
   - Mark slow tests with @pytest.mark.slow
   - Use fixtures for expensive setup

8. Test Maintenance:
   - Keep tests simple and readable
   - Avoid test interdependencies
   - Use descriptive assertions
   - Update tests with code changes
"""
