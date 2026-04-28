"""
WCAG compliance levels and accessibility utilities.
"""

from enum import Enum


class WCAGLevel(Enum):
    """
    WCAG contrast compliance levels.
    """

    AA_NORMAL = 4.5  # AA for normal text
    AA_LARGE = 3.0  # AA for large text (18pt+)
    AAA_NORMAL = 7.0  # AAA for normal text
    AAA_LARGE = 4.5  # AAA for large text
