"""
Carrier Registry — factory for getting the right connector per carrier.

When USE_MOCK_CARRIERS=true, returns MockCarrierConnector.
When false, returns the live connector or NotAvailableConnector.
"""
import os
from carriers.base_connector import BaseCarrierConnector, NotAvailableConnector
from carriers.mock_connector import MockCarrierConnector
from carriers.maersk_connector import MaerskConnector
from carriers.one_connector import ONEConnector
from carriers.cma_connector import CMAConnector
from carriers.hapag_lloyd_connector import HapagLloydConnector
from carriers.greenx_connector import GreenXConnector
from carriers.msc_connector import MSCConnector
from carriers.oocl_connector import OOCLConnector


# Map carrier codes to their live connector classes
LIVE_CONNECTORS: dict[str, type[BaseCarrierConnector]] = {
    "MAERSK": MaerskConnector,
    "ONE": ONEConnector,
    "CMA_CGM": CMAConnector,
    "HAPAG_LLOYD": HapagLloydConnector,
    "GREENX": GreenXConnector,
    "MSC": MSCConnector,
    "OOCL": OOCLConnector,
}

# All supported carrier codes
SUPPORTED_CARRIERS = [
    "MAERSK", "ONE", "CMA_CGM", "HAPAG_LLOYD", "OOCL", "GREENX", "MSC"
]


def get_connector(carrier_code: str) -> BaseCarrierConnector:
    """
    Get the appropriate connector for a carrier.

    If USE_MOCK_CARRIERS=true: returns MockCarrierConnector
    If live mode: returns the live connector or NotAvailableConnector
    """
    use_mock = os.getenv("USE_MOCK_CARRIERS", "true").lower() in ("true", "1", "yes")

    if use_mock:
        return MockCarrierConnector(carrier_code)

    # Live mode
    if carrier_code in LIVE_CONNECTORS:
        return LIVE_CONNECTORS[carrier_code]()

    return NotAvailableConnector(carrier_code)
