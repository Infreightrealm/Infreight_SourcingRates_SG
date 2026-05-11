"""OOCL Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class OOCLConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("OOCL")
        self.carrier_name = "Orient Overseas Container Line"
