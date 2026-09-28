"""
Carrier Registry — factory for getting the right connector per carrier.

When USE_MOCK_CARRIERS=true, returns MockCarrierConnector.
When false, returns the live connector or NotAvailableConnector.
"""
import os
from typing import Optional
from carriers.base_connector import BaseCarrierConnector, NotAvailableConnector
from carriers.mock_connector import MockCarrierConnector
from carriers.maersk_connector import MaerskConnector
from carriers.one_connector import ONEConnector
from carriers.cma_connector import CMAConnector
from carriers.hapag_lloyd_connector import HapagLloydConnector
from carriers.hapag_lloyd_api_connector import HapagLloydAPIConnector
from carriers.greenx_connector import GreenXConnector
from carriers.msc_connector import MSCConnector
from carriers.oocl_connector import OOCLConnector


# Map carrier codes to their live connector classes
LIVE_CONNECTORS: dict[str, type[BaseCarrierConnector]] = {
    "MAERSK": MaerskConnector,
    "ONE": ONEConnector,
    "CMA_CGM": CMAConnector,
    "HAPAG_LLOYD": HapagLloydConnector,
    "HAPAG_LLOYD_API": HapagLloydAPIConnector,
    "GREENX": GreenXConnector,
    "MSC": MSCConnector,
    "OOCL": OOCLConnector,
}

# All supported carrier codes
SUPPORTED_CARRIERS = [
    "MAERSK", "ONE", "CMA_CGM", "HAPAG_LLOYD", "HAPAG_LLOYD_API", "OOCL", "GREENX", "MSC"
]


# Active connector instance registry for force-stop teardown
ACTIVE_CONNECTOR_INSTANCES: dict[str, BaseCarrierConnector] = {}


def get_connector(carrier_code: str, hapag_use_api: Optional[bool] = None) -> BaseCarrierConnector:
    """
    Get the appropriate connector for a carrier.

    If USE_MOCK_CARRIERS=true: returns MockCarrierConnector
    If live mode: returns the live connector or NotAvailableConnector

    hapag_use_api: per-search Hapag-Lloyd source (True = Prices API, False = portal scraping);
    None falls back to the HAPAG_USE_API environment variable.
    """
    use_mock = os.getenv("USE_MOCK_CARRIERS", "true").lower() in ("true", "1", "yes")

    if use_mock:
        conn = MockCarrierConnector(carrier_code)
        ACTIVE_CONNECTOR_INSTANCES[carrier_code] = conn
        return conn

    if hapag_use_api is None:
        hapag_use_api = os.getenv("HAPAG_USE_API", "false").lower() in ("true", "1", "yes")
    if carrier_code == "HAPAG_LLOYD" and hapag_use_api:
        conn = HapagLloydAPIConnector()
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
