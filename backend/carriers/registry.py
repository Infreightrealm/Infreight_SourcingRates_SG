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


# Active connector instance registry for force-stop teardown
ACTIVE_CONNECTOR_INSTANCES: dict[str, BaseCarrierConnector] = {}


def get_connector(carrier_code: str) -> BaseCarrierConnector:
    """
    Get the appropriate connector for a carrier.

    If USE_MOCK_CARRIERS=true: returns MockCarrierConnector
    If live mode: returns the live connector or NotAvailableConnector
    """
    use_mock = os.getenv("USE_MOCK_CARRIERS", "true").lower() in ("true", "1", "yes")

    if use_mock:
        conn = MockCarrierConnector(carrier_code)
        ACTIVE_CONNECTOR_INSTANCES[carrier_code] = conn
        return conn

    # Live mode
    if carrier_code in LIVE_CONNECTORS:
        conn = LIVE_CONNECTORS[carrier_code]()
        ACTIVE_CONNECTOR_INSTANCES[carrier_code] = conn
        return conn

    conn = NotAvailableConnector(carrier_code)
    ACTIVE_CONNECTOR_INSTANCES[carrier_code] = conn
    return conn


async def close_all_active_connectors():
    """Force close all active carrier connectors and their Playwright Chrome windows."""
    for carrier_code, connector in list(ACTIVE_CONNECTOR_INSTANCES.items()):
        try:
            print(f"[REGISTRY] Force closing active browser for {carrier_code}...")
            connector.is_batch_active = False
            await connector.close(force=True)
        except Exception as e:
            print(f"[REGISTRY] Error force closing {carrier_code}: {e}")
    ACTIVE_CONNECTOR_INSTANCES.clear()
