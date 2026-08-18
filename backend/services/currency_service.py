"""
Currency Exchange Rate Service — manages currency conversions and custom exchange rates.
Stores persistence in backend/data/exchange_rates_config.json
"""
import json
import os
import threading
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CONFIG_PATH = os.path.join(DATA_DIR, "exchange_rates_config.json")

_lock = threading.Lock()

DEFAULT_EXCHANGE_RATES: Dict[str, Dict[str, Any]] = {
    "USD": {"name": "US Dollar", "rate_per_usd": 1.0, "symbol": "$"},
    "INR": {"name": "Indian Rupee", "rate_per_usd": 86.5, "symbol": "₹"},
    "SGD": {"name": "Singapore Dollar", "rate_per_usd": 1.35, "symbol": "S$"},
    "EUR": {"name": "Euro", "rate_per_usd": 0.92, "symbol": "€"},
    "GBP": {"name": "British Pound", "rate_per_usd": 0.78, "symbol": "£"},
    "MYR": {"name": "Malaysian Ringgit", "rate_per_usd": 4.45, "symbol": "RM"},
    "THB": {"name": "Thai Baht", "rate_per_usd": 36.5, "symbol": "฿"},
    "AUD": {"name": "Australian Dollar", "rate_per_usd": 1.52, "symbol": "A$"},
    "CNY": {"name": "Chinese Yuan", "rate_per_usd": 7.25, "symbol": "¥"},
    "JPY": {"name": "Japanese Yen", "rate_per_usd": 155.0, "symbol": "¥"},
    "HKD": {"name": "Hong Kong Dollar", "rate_per_usd": 7.82, "symbol": "HK$"},
    "AED": {"name": "UAE Dirham", "rate_per_usd": 3.67, "symbol": "AED"},
    "VND": {"name": "Vietnamese Dong", "rate_per_usd": 25400.0, "symbol": "₫"},
    "IDR": {"name": "Indonesian Rupiah", "rate_per_usd": 16200.0, "symbol": "Rp"},
    "CAD": {"name": "Canadian Dollar", "rate_per_usd": 1.38, "symbol": "C$"},
    "NZD": {"name": "New Zealand Dollar", "rate_per_usd": 1.68, "symbol": "NZ$"},
}


class CurrencyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        self.rates = json.loads(json.dumps(DEFAULT_EXCHANGE_RATES))
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        for code, info in saved.items():
                            code_u = code.upper()
                            if code_u in self.rates and isinstance(info, dict) and "rate_per_usd" in info:
                                self.rates[code_u]["rate_per_usd"] = float(info["rate_per_usd"])
                            elif isinstance(info, (int, float)):
                                if code_u in self.rates:
                                    self.rates[code_u]["rate_per_usd"] = float(info)
                                else:
                                    self.rates[code_u] = {
                                        "name": code_u,
                                        "rate_per_usd": float(info),
                                        "symbol": code_u,
                                    }
            except Exception as e:
                print(f"[CURRENCY] Error loading {CONFIG_PATH}: {e}")

    def save_config(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.rates, f, indent=2)
        except Exception as e:
            print(f"[CURRENCY] Error saving {CONFIG_PATH}: {e}")

    def get_rates(self) -> Dict[str, Dict[str, Any]]:
        with _lock:
            # Add calculated rate_to_usd for convenience (1 local = X USD)
            res = {}
            for code, info in self.rates.items():
                rate = float(info.get("rate_per_usd", 1.0))
                rate_to_usd = round(1.0 / rate, 6) if rate > 0 else 1.0
                res[code] = {
                    "code": code,
                    "name": info.get("name", code),
                    "rate_per_usd": rate,       # e.g. 1 USD = 86.5 INR
                    "usd_per_unit": rate_to_usd, # e.g. 1 INR = 0.01156 USD
                    "symbol": info.get("symbol", "$"),
                }
            return res

    def update_rate(self, currency_code: str, rate_per_usd: float) -> Dict[str, Any]:
        with _lock:
            code_u = currency_code.upper().strip()
            if rate_per_usd <= 0:
                raise ValueError("Exchange rate must be greater than 0")
            if code_u not in self.rates:
                self.rates[code_u] = {
                    "name": code_u,
                    "rate_per_usd": float(rate_per_usd),
                    "symbol": code_u,
                }
            else:
                self.rates[code_u]["rate_per_usd"] = float(rate_per_usd)
            self.save_config()
            return self.get_rates()[code_u]

    def convert_to_usd(self, amount: float, currency: str) -> float:
        with _lock:
            code_u = (currency or "USD").upper().strip()
            if code_u == "USD" or amount == 0:
                return amount
            info = self.rates.get(code_u)
            if not info or info.get("rate_per_usd", 0) <= 0:
                return amount  # fallback unchanged
            return round(amount / float(info["rate_per_usd"]), 2)


def get_all_exchange_rates() -> Dict[str, Dict[str, Any]]:
    return CurrencyManager().get_rates()


def update_exchange_rate(currency_code: str, rate_per_usd: float) -> Dict[str, Any]:
    return CurrencyManager().update_rate(currency_code, rate_per_usd)


def convert_currency_to_usd(amount: float, currency: str) -> float:
    return CurrencyManager().convert_to_usd(amount, currency)
