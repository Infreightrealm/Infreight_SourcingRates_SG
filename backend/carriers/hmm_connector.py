"""HMM Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class HMMConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("HMM")
        self.carrier_name = "HMM (Hyundai Merchant Marine)"
