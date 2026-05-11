"""CMA CGM Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE."""
from carriers.base_connector import NotAvailableConnector

class CMACGMConnector(NotAvailableConnector):
    def __init__(self):
        super().__init__("CMA_CGM")
        self.carrier_name = "CMA CGM"
