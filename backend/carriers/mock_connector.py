"""
Mock Carrier Connector — returns realistic sample data for testing.

Used when USE_MOCK_CARRIERS=true.
Returns sample Maersk and ONE quote data that flows through
the same normalizer and charge classifier pipeline.
"""
from datetime import datetime, timedelta
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from services.normalizer import normalize_quote
from carriers.base_connector import BaseCarrierConnector


# ────────────────────────────────────────────
# Sample data generators
# ────────────────────────────────────────────

def _generate_maersk_mock_quotes(request: RateSearchRequest) -> list[tuple[dict, list[dict]]]:
    """Generate realistic Maersk sample quotes with charge breakdowns."""
    base_date = datetime.now() + timedelta(days=1)

    quotes = [
        # Quote 1: Direct service
        (
            {
                "etd": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=30)).strftime("%Y-%m-%d"),
                "transit_time_days": 28,
                "service_name": "AE7 - Asia to Europe",
                "vessel": "Maersk Edinburgh",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "MAERSK-MOCK-001",
            },
            [
                {"name": "Basic Ocean Freight", "amount": 1450.00, "currency": "USD"},
                {"name": "Maersk Discount", "amount": -100.00, "currency": "USD"},
                {"name": "Emergency Fuel Surcharge", "amount": 165.00, "currency": "USD"},
                {"name": "Europe Environment Surcharge", "amount": 85.00, "currency": "USD"},
                {"name": "Low Sulphur Surcharge", "amount": 120.00, "currency": "USD"},
                {"name": "Peak Season Surcharge", "amount": 200.00, "currency": "USD"},
                {"name": "Origin THC", "amount": 280.00, "currency": "USD"},
                {"name": "Destination THC", "amount": 320.00, "currency": "USD"},
                {"name": "Documentation Fee", "amount": 50.00, "currency": "USD"},
                {"name": "ISPS Fee", "amount": 15.00, "currency": "USD"},
            ],
        ),
        # Quote 2: Transshipment service
        (
            {
                "etd": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=38)).strftime("%Y-%m-%d"),
                "transit_time_days": 33,
                "service_name": "AE1 - Asia Europe Express",
                "vessel": "Maersk Sentosa",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "MAERSK-MOCK-002",
            },
            [
                {"name": "Basic Ocean Freight", "amount": 1280.00, "currency": "USD"},
                {"name": "Volume Discount", "amount": -50.00, "currency": "USD"},
                {"name": "Emergency Fuel Surcharge", "amount": 155.00, "currency": "USD"},
                {"name": "Europe Environment Surcharge", "amount": 85.00, "currency": "USD"},
                {"name": "Low Sulphur Surcharge", "amount": 110.00, "currency": "USD"},
                {"name": "Bunker Adjustment Factor", "amount": 95.00, "currency": "USD"},
                {"name": "Origin THC", "amount": 280.00, "currency": "USD"},
                {"name": "Destination THC", "amount": 320.00, "currency": "USD"},
                {"name": "Seal Fee", "amount": 20.00, "currency": "USD"},
            ],
        ),
        # Quote 3: Budget option
        (
            {
                "etd": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=44)).strftime("%Y-%m-%d"),
                "transit_time_days": 35,
                "service_name": "AE55 - Asia to North Europe",
                "vessel": "Maersk Seletar",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "MAERSK-MOCK-003",
            },
            [
                {"name": "Basic Ocean Freight", "amount": 1100.00, "currency": "USD"},
                {"name": "Emergency Fuel Surcharge", "amount": 145.00, "currency": "USD"},
                {"name": "Europe Environment Surcharge", "amount": 85.00, "currency": "USD"},
                {"name": "Low Sulphur Surcharge", "amount": 105.00, "currency": "USD"},
                {"name": "War Risk Surcharge", "amount": 45.00, "currency": "USD"},
                {"name": "Origin THC", "amount": 280.00, "currency": "USD"},
                {"name": "Destination THC", "amount": 320.00, "currency": "USD"},
                {"name": "Documentation Fee", "amount": 50.00, "currency": "USD"},
                {"name": "Container Cleaning Fee", "amount": 35.00, "currency": "USD"},
            ],
        ),
    ]
    return quotes


def _generate_one_mock_quotes(request: RateSearchRequest) -> list[tuple[dict, list[dict]]]:
    """Generate realistic ONE sample quotes with charge breakdowns."""
    base_date = datetime.now() + timedelta(days=1)

    quotes = [
        # Quote 1
        (
            {
                "etd": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=32)).strftime("%Y-%m-%d"),
                "transit_time_days": 29,
                "service_name": "FE4 - Far East to Europe",
                "vessel": "ONE Competence",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "ONE-MOCK-001",
            },
            [
                {"name": "Ocean Freight", "amount": 1380.00, "currency": "USD"},
                {"name": "ONE Bunker Surcharge", "amount": 175.00, "currency": "USD"},
                {"name": "Emergency Fuel Surcharge", "amount": 140.00, "currency": "USD"},
                {"name": "Europe Environment Surcharge", "amount": 90.00, "currency": "USD"},
                {"name": "Low Sulphur Surcharge", "amount": 115.00, "currency": "USD"},
                {"name": "Peak Season Surcharge", "amount": 180.00, "currency": "USD"},
                {"name": "Origin THC", "amount": 265.00, "currency": "USD"},
                {"name": "Destination THC", "amount": 310.00, "currency": "USD"},
                {"name": "Documentation Fee", "amount": 45.00, "currency": "USD"},
                {"name": "VGM Fee", "amount": 25.00, "currency": "USD"},
            ],
        ),
        # Quote 2
        (
            {
                "etd": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=39)).strftime("%Y-%m-%d"),
                "transit_time_days": 32,
                "service_name": "FE2 - Far East Express",
                "vessel": "ONE Contribution",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "ONE-MOCK-002",
            },
            [
                {"name": "Ocean Freight", "amount": 1220.00, "currency": "USD"},
                {"name": "Rebate", "amount": -75.00, "currency": "USD"},
                {"name": "ONE Bunker Surcharge", "amount": 160.00, "currency": "USD"},
                {"name": "Emergency Fuel Surcharge", "amount": 130.00, "currency": "USD"},
                {"name": "Low Sulphur Surcharge", "amount": 100.00, "currency": "USD"},
                {"name": "Europe Environment Surcharge", "amount": 90.00, "currency": "USD"},
                {"name": "Origin THC", "amount": 265.00, "currency": "USD"},
                {"name": "Destination THC", "amount": 310.00, "currency": "USD"},
                {"name": "Export Documentation Fee", "amount": 45.00, "currency": "USD"},
            ],
        ),
    ]
    return quotes


def _generate_msc_mock_quotes(request: RateSearchRequest) -> list[tuple[dict, list[dict]]]:
    """Generate realistic MSC sample quotes with validity_till."""
    base_date = datetime.now() + timedelta(days=1)
    expiration_date = (base_date + timedelta(days=5)).strftime("%Y-%m-%d")

    quotes = [
        (
            {
                "etd": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "eta": (base_date + timedelta(days=32)).strftime("%Y-%m-%d"),
                "transit_time_days": 29,
                "service_name": "Lion Service",
                "vessel": "MSC OSCAR",
                "container_type": request.container_type,
                "container_quantity": request.container_quantity,
                "currency": "USD",
                "source": "mock",
                "raw_reference": "MSC-MOCK-001",
                "validity_till": expiration_date,
            },
            [
                {"name": "Basic Ocean Freight", "amount": 1650.00, "currency": "USD"},
                {"name": "MSC Surcharges", "amount": 150.00, "currency": "USD"},
            ],
        ),
    ]
    return quotes


# ────────────────────────────────────────────

# Mock Connector
# ────────────────────────────────────────────

class MockCarrierConnector(BaseCarrierConnector):
    """
    Mock connector that returns realistic sample data.
    Data passes through the same normalizer/classifier pipeline as real data.
    """

    def __init__(self, carrier_code: str):
        super().__init__()
        self.carrier_code = carrier_code
        self.carrier_name = carrier_code.replace("_", " ").title()

    async def login(self) -> bool:
        return True

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

    async def extract_quote_list(self) -> list[dict]:
        return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return True

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        return normalize_quote(self.carrier_code, raw_quote, raw_charges)

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        Override to return mock data through the normalizer pipeline.
        """
        # Select mock data based on carrier
        if self.carrier_code == "MAERSK":
            mock_data = _generate_maersk_mock_quotes(request)
        elif self.carrier_code == "ONE":
            mock_data = _generate_one_mock_quotes(request)
        elif self.carrier_code == "MSC":
            mock_data = _generate_msc_mock_quotes(request)
        else:
            # Other carriers in mock mode: return not available
            return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, []


        quotes = []
        for raw_quote, raw_charges in mock_data:
            normalized = await self.normalize_result(raw_quote, raw_charges)
            quotes.append(normalized)

        if quotes:
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
        return CarrierResultStatus.NO_QUOTES_AVAILABLE, []
