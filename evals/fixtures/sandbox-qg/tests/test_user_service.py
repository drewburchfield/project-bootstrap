"""Incomplete tests — compute_score intentionally uncovered."""

from src.user_service import format_display_name


def test_format_display_name_happy():
    assert format_display_name({"name": "ada"}) == "ADA"
