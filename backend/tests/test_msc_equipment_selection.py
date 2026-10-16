import pytest
from unittest.mock import AsyncMock, MagicMock
from carriers.msc_connector import (
    MSCConnector,
    map_requested_containers_to_msc_sizes,
    is_same_container_type,
)
from models.schemas import RateSearchRequest


def test_map_requested_containers_to_msc_sizes():
    # Single 20ft selections
    assert map_requested_containers_to_msc_sizes(container_types=["20GP"]) == {"20DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 20"]) == {"20DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["20DV"]) == {"20DV"}
    assert map_requested_containers_to_msc_sizes(container_type="20GP") == {"20DV"}
    assert map_requested_containers_to_msc_sizes(container_type="DRY 20") == {"20DV"}

    # Single 40ft standard selections
    assert map_requested_containers_to_msc_sizes(container_types=["40GP"]) == {"40DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 40"]) == {"40DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["40DV"]) == {"40DV"}
    assert map_requested_containers_to_msc_sizes(container_type="40GP") == {"40DV"}

    # Single 40ft High Cube selections
    assert map_requested_containers_to_msc_sizes(container_types=["40HQ"]) == {"40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["40HC"]) == {"40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 40H"]) == {"40HC"}
    assert map_requested_containers_to_msc_sizes(container_type="40HQ") == {"40HC"}
    assert map_requested_containers_to_msc_sizes(container_type="DRY 40H") == {"40HC"}

    # Multi-container combinations
    assert map_requested_containers_to_msc_sizes(container_types=["20GP", "40GP"]) == {"20DV", "40DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 20", "DRY 40"]) == {"20DV", "40DV"}
    assert map_requested_containers_to_msc_sizes(container_types=["20GP", "40HQ"]) == {"20DV", "40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 20", "DRY 40H"]) == {"20DV", "40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["40GP", "40HQ"]) == {"40DV", "40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["20GP", "40GP", "40HQ"]) == {"20DV", "40DV", "40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=["DRY 20", "DRY 40", "DRY 40H"]) == {"20DV", "40DV", "40HC"}

    # Empty / None fallback
    assert map_requested_containers_to_msc_sizes(container_types=[]) == {"20DV", "40DV", "40HC"}
    assert map_requested_containers_to_msc_sizes(container_types=None, container_type=None) == {"20DV", "40DV", "40HC"}


def test_is_same_container_type():
    assert is_same_container_type("DRY 20", "20GP") is True
    assert is_same_container_type("20GP", "20DV") is True
    assert is_same_container_type("DRY 40", "40GP") is True
    assert is_same_container_type("DRY 40H", "40HQ") is True
    assert is_same_container_type("40HC", "40HQ") is True
    assert is_same_container_type("DRY 20", "DRY 40") is False
    assert is_same_container_type("20GP", "40HQ") is False


@pytest.mark.asyncio
async def test_set_msc_equipment_sizes_only_20gp():
    """
    Simulates Singapore to Brisbane where the user only selected 20GP on the frontend.
    Verifies that 40DV and 40HC checkboxes are unchecked, leaving only 20DV selected.
    """
    connector = MSCConnector()
    mock_page = AsyncMock()
    connector.page = mock_page

    # Simulate checkbox states in page DOM:
    # MSC defaults to all 3 checked (20DV, 40DV, 40HC)
    checkbox_states = {
        "20DV": True,
        "40DV": True,
        "40HC": True,
    }

    clicked_elements = []

    async def mock_evaluate(script, arg):
        if isinstance(arg, str):
            # Checking initial state for a size code
            code = arg
            return {"found": True, "checked": checkbox_states[code]}
        elif isinstance(arg, list):
            # Verification / JS fallback after click: [code, expected]
            code, expected = arg[0], arg[1]
            return {"verified": True, "checked": checkbox_states[code]}
        return {}

    mock_page.evaluate = AsyncMock(side_effect=mock_evaluate)

    # Mock locator for each code
    def make_mock_locator(selector):
        loc = MagicMock()
        loc.count = AsyncMock(return_value=1)

        el = AsyncMock()
        el.is_visible = AsyncMock(return_value=True)

        input_child = MagicMock()
        input_child.count = AsyncMock(return_value=1)
        input_first = AsyncMock()
        input_first.is_visible = AsyncMock(return_value=True)

        async def input_click(force=True):
            for code in ("20DV", "40DV", "40HC"):
                if code in selector:
                    clicked_elements.append(code)
                    checkbox_states[code] = not checkbox_states[code]

        input_first.click = AsyncMock(side_effect=input_click)
        input_child.first = input_first
        el.locator = MagicMock(return_value=input_child)
        el.click = AsyncMock(side_effect=input_click)
        loc.first = el
        return loc

    mock_page.locator = MagicMock(side_effect=make_mock_locator)

    request = RateSearchRequest(
        carriers=["MSC"],
        origin="Singapore",
        destination="Brisbane, Australia",
        container_types=["DRY 20"],  # User only selected 20GP (DRY 20)
        container_type="DRY 20",
    )

    target_sizes = await connector._set_msc_equipment_sizes(request)

    assert target_sizes == {"20DV"}
    # 20DV should NOT have been clicked (it was already checked)
    assert "20DV" not in clicked_elements
    # 40DV and 40HC should have been clicked to uncheck them
    assert "40DV" in clicked_elements
    assert "40HC" in clicked_elements
    # Resulting states
    assert checkbox_states["20DV"] is True
    assert checkbox_states["40DV"] is False
    assert checkbox_states["40HC"] is False


@pytest.mark.asyncio
async def test_set_msc_equipment_sizes_multi_selection():
    """
    Simulates a search where the user selected 20GP and 40HQ.
    Verifies that 40DV is unchecked, while 20DV and 40HC remain checked.
    """
    connector = MSCConnector()
    mock_page = AsyncMock()
    connector.page = mock_page

    checkbox_states = {
        "20DV": True,
        "40DV": True,
        "40HC": True,
    }

    clicked_elements = []

    async def mock_evaluate(script, arg):
        if isinstance(arg, str):
            code = arg
            return {"found": True, "checked": checkbox_states[code]}
        elif isinstance(arg, list):
            code, expected = arg[0], arg[1]
            return {"verified": True, "checked": checkbox_states[code]}
        return {}

    mock_page.evaluate = AsyncMock(side_effect=mock_evaluate)

    def make_mock_locator(selector):
        loc = MagicMock()
        loc.count = AsyncMock(return_value=1)

        el = AsyncMock()
        el.is_visible = AsyncMock(return_value=True)

        input_child = MagicMock()
        input_child.count = AsyncMock(return_value=1)
        input_first = AsyncMock()
        input_first.is_visible = AsyncMock(return_value=True)

        async def input_click(force=True):
            for code in ("20DV", "40DV", "40HC"):
                if code in selector:
                    clicked_elements.append(code)
                    checkbox_states[code] = not checkbox_states[code]

        input_first.click = AsyncMock(side_effect=input_click)
        input_child.first = input_first
        el.locator = MagicMock(return_value=input_child)
        el.click = AsyncMock(side_effect=input_click)
        loc.first = el
        return loc

    mock_page.locator = MagicMock(side_effect=make_mock_locator)

    request = RateSearchRequest(
        carriers=["MSC"],
        origin="Singapore",
        destination="Brisbane, Australia",
        container_types=["20GP", "40HQ"],
    )

    target_sizes = await connector._set_msc_equipment_sizes(request)

    assert target_sizes == {"20DV", "40HC"}
    assert "20DV" not in clicked_elements
    assert "40HC" not in clicked_elements
    assert "40DV" in clicked_elements
    assert checkbox_states["20DV"] is True
    assert checkbox_states["40DV"] is False
    assert checkbox_states["40HC"] is True
