"""Hapag-Lloyd Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class HapagLloydConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("HAPAG_LLOYD")
        self.carrier_name = "Hapag-Lloyd"
