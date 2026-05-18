import json
import os
import re
from difflib import get_close_matches
from typing import List, Dict, Optional

class PortManager:
    _instance = None
    _ports = {}
    _aliases = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortManager, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "port_codes.json")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._ports = data.get("ports", {})
                self._aliases = data.get("aliases", {})
        except Exception as e:
            print(f"Error loading port data: {e}")
            self._ports = {}
            self._aliases = {}

    def normalize_port_input(self, text: str) -> str:
        """Clean and normalize user input for port searching."""
        if not text:
            return ""
        # Remove common fluff
        text = text.lower().strip()
        text = re.sub(r'\b(port|of|terminal|container)\b', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_port_by_code(self, code: str) -> Optional[Dict]:
        """Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')."""
        return self._ports.get(code.upper())

    def search_port(self, query: str, country: Optional[str] = None) -> List[Dict]:
        """
        Search for ports by code, name, or alias.
        Returns top matches ranked by relevance.
        """
        query_norm = self.normalize_port_input(query)
        if not query_norm:
            return []

        results = []
        seen_codes = set()

        # 1. Exact full code match
        direct_match = self.get_port_by_code(query.upper())
        if direct_match:
            results.append((direct_match, 0)) # Rank 0 (top)
            seen_codes.add(direct_match['code'])

        # 2. Exact alias match (names, common formats)
        matches = self._aliases.get(query_norm, [])
        for code in matches:
            if code not in seen_codes:
                port = self._ports.get(code)
                if port:
                    # Filter by country if provided
                    if country and port['country'].upper() != country.upper():
                        continue
                    results.append((port, 1))
                    seen_codes.add(code)

        # 3. Fuzzy match on alias keys if no results yet
        if not results:
            alias_keys = list(self._aliases.keys())
            close_aliases = get_close_matches(query_norm, alias_keys, n=10, cutoff=0.7)
            for alias in close_aliases:
                for code in self._aliases[alias]:
                    if code not in seen_codes:
                        port = self._ports.get(code)
                        if port:
                            if country and port['country'].upper() != country.upper():
                                continue
                            results.append((port, 2))
                            seen_codes.add(code)

        # 4. Partial name match
        if len(results) < 10:
            for code, port in self._ports.items():
                if code in seen_codes:
                    continue
                if query_norm in port['name'].lower() or query_norm in port['name_ascii'].lower():
                    if country and port['country'].upper() != country.upper():
                        continue
                    results.append((port, 3))
                    seen_codes.add(code)
                if len(results) >= 20:
                    break

        # Sorting logic:
        # Rank by score (lower is better), then by status confidence
        def ranking_key(item):
            port, score = item
            # Status confidence: AI (Approved) > RL (Recognized) > others
            status_score = 0
            if port['status'] == 'AI': status_score = 0
            elif port['status'] == 'RL': status_score = 1
            else: status_score = 2
            
            return (score, status_score, port['name'])

        results.sort(key=ranking_key)
        return [r[0] for r in results]

    def suggest_ports(self, query: str, limit: int = 5) -> List[Dict]:
        """Suggest top N ports for a partial query."""
        results = self.search_port(query)
        return results[:limit]

# Convenience functions
def get_port_by_code(code: str):
    return PortManager().get_port_by_code(code)

def search_port(query: str, country: str = None):
    return PortManager().search_port(query, country)

def normalize_port_input(text: str):
    return PortManager().normalize_port_input(text)

def suggest_ports(query: str, limit: int = 5):
    return PortManager().suggest_ports(query, limit)
