"""COSCO Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class COSCOConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("COSCO")
        self.carrier_name = "COSCO Shipping"
