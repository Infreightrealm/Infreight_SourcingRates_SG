"""MSC Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class MSCConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("MSC")
        self.carrier_name = "Mediterranean Shipping Company"
