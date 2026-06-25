"""
Unit tests for multiple container type search validation and schemas.
"""
import sys
import os

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import RateSearchRequest


def test_request_validation_only_type():
    # Test when only container_type is provided (backward compatibility)
    req = RateSearchRequest.model_validate({
        "carriers": ["MAERSK"],
        "origin": "Singapore",
        "destination": "Hamburg",
        "container_type": "DRY 20",
        "container_quantity": 1,
        "weight_per_container_kg": 20000,
        "commodity": "Furniture",
        "departure_date": "tomorrow",
        "search_window_days": 14
    })
    assert req.container_type == "DRY 20"
    assert req.container_types == ["DRY 20"]


def test_request_validation_types_list():
    # Test when container_types is provided as list
    req = RateSearchRequest.model_validate({
        "carriers": ["MAERSK"],
        "origin": "Singapore",
        "destination": "Hamburg",
        "container_types": ["DRY 20", "DRY 40H"],
        "container_quantity": 1,
        "weight_per_container_kg": 20000,
        "commodity": "Furniture",
        "departure_date": "tomorrow",
        "search_window_days": 14
    })
    assert req.container_type == "DRY 20"
    assert req.container_types == ["DRY 20", "DRY 40H"]


def test_request_validation_types_comma_string():
    # Test when container_types is provided as comma-separated string
    req = RateSearchRequest.model_validate({
        "carriers": ["MAERSK"],
        "origin": "Singapore",
        "destination": "Hamburg",
        "container_types": "DRY 20, DRY 40, DRY 40H",
        "container_quantity": 1,
        "weight_per_container_kg": 20000,
        "commodity": "Furniture",
        "departure_date": "tomorrow",
        "search_window_days": 14
    })
    assert req.container_type == "DRY 20"
    assert req.container_types == ["DRY 20", "DRY 40", "DRY 40H"]


def test_request_validation_defaults():
    # Test defaults
    req = RateSearchRequest.model_validate({
        "carriers": ["MAERSK"],
        "origin": "Singapore",
        "destination": "Hamburg"
    })
    assert req.container_type == "DRY 40H"
    assert req.container_types == ["DRY 40H"]


if __name__ == "__main__":
    test_request_validation_only_type()
    test_request_validation_types_list()
    test_request_validation_types_comma_string()
    test_request_validation_defaults()
    print("All multi-container request validation tests passed successfully!")
