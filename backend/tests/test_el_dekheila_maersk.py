import pytest
from services.port_manager import resolve_port_for_carrier, CARRIER_PORT_OVERRIDES

def test_el_dekheila_maersk_override():
    """Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for Maersk only."""
    assert resolve_port_for_carrier("El Dekheila", "maersk") == "Alexandria Dekheila, Egypt"
    assert resolve_port_for_carrier("dekheila", "maersk") == "Alexandria Dekheila, Egypt"
    assert resolve_port_for_carrier("EGEDK", "maersk") == "Alexandria Dekheila, Egypt"
    assert CARRIER_PORT_OVERRIDES["maersk"]["EGEDK"] == "Alexandria Dekheila, Egypt"

def test_el_dekheila_other_carriers_unaffected():
    """Verify non-Maersk carriers get standard UN/LOCODE or default mappings."""
    assert resolve_port_for_carrier("El Dekheila", "cma") == "EGEDK"
    assert resolve_port_for_carrier("El Dekheila", "greenx") == "EGEDK"
