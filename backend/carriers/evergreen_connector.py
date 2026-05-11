"""Evergreen Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class EvergreenConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("EVERGREEN")
        self.carrier_name = "Evergreen Marine"
