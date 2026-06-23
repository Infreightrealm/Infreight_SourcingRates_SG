import json
import os
import re
from difflib import get_close_matches
from typing import List, Dict, Optional

CARRIER_PORT_OVERRIDES = {
    "maersk": {
        "VNHPH": "Haiphong",
        "VNSGN": "Ho Chi Minh",        # shorter query triggers dropdown better than "Ho Chi Minh City"
        "SGSIN": "Singapore",
        "DEHAM": "Hamburg",
        "MYLPK": "Port Klang",
        "MYPKG": "Port Klang",
        "TWKHH": "Kaohsiung",
        "TWKEL": "Keelung",
        "CNSHA": "Shanghai",
        "CNSZX": "Shenzhen (Guangdong), China",
        "CNNGB": "Ningbo (Zhejiang), China",
        "PKKHI": "Karachi",
        "INNSA": "Jawaharlal Nehru (MAHARASHTRA), India",
        "SAJED": "Jeddah, Saudi Arabia",
        "EGAIS": "Ain Sukhna, Egypt",
        "EGALX": "Alexandria, Egypt",
        "EGALY": "Alexandria, Egypt",
        "IDJKT": "Jakarta",
        "IDBTM": "Batam",
        "IDSUB": "Surabaya",
        "AUMEL": "Melbourne",
        "AUSYD": "Sydney (New South Wales), Australia",
        "THBKK": "Bangkok PAT, Thailand",
        "THLCH": "Laem Chabang",
        # New port mappings requested
        "YEADE": "Aden, Yemen",
        "KHKOS": "Sihanoukville, Cambodia",
        "CASHV": "Sihanoukville, Cambodia",
        "MYPEN": "Penang (Pulau Pinang), Malaysia",
        "MYPGU": "Pasir Gudang (Johor), Malaysia",
        "MYTPP": "Tanjung Pelepas (Johor), Malaysia",
        "CNTAO": "Qingdao (Shandong), China",
        "TWTXG": "Taichung, Taiwan China",
        "VNVUT": "Vung Tau (Ba Ria - Vung Tau), Vietnam",
        "INMAA": "Chennai (TAMIL NADU), India",
        "AEJEA": "Jebel Ali, United Arab Emirates",
        "OMSOH": "Sohar, Oman",
        "EGSOK": "Sokhna, Egypt",
        "IDSRG": "Semarang, Indonesia",
        "THLKR": "Lat Krabang, Thailand",
        "KNPNH": "Phnom Penh, Cambodia",
        "TLDIL": "Dili, Timor Leste",
        "CNXMN": "Xiamen (Fujian), China",
    },
    "one": {
        "VNHPH": "Hai Phong",
        "VNSGN": "Ho Chi Minh",
        "SGSIN": "Singapore",
        "DEHAM": "Hamburg",
        "MYLPK": "Port Klang",
        "MYPKG": "Port Klang",
        "PKKHI": "Karachi",
        "INNSA": "Nhava Sheva",
        "AUMEL": "Melbourne",
        "CNXMN": "Xiamen",
    },
    "greenx": {
        # GreenX autocomplete accepts LOCODE directly (e.g. SGSIN, DEHAM)
        # No name translation needed — type LOCODE, click first matching option
    }
}

PORT_MAP_CMA_ONE = {
    "MYPKG": "MYPKG",
    "TWKHH": "TWKHH",
    "TWKEL": "TWKEL",
    "CNSHA": "CNSHA",
    "CNSZX": "CNSZX",
    "CNNGB": "CNNGB",
    "VNSGN": "VNSGN",
    "VNHPH": "VNHPH",
    "PKKHI": "PKKHI",
    "INNSA": "INNSA",
    "SAJED": "SAJED",
    "EGAIS": "EGAIS",
    "IDJKT": "IDJKT",
    "IDBTM": "IDBTM",
    "IDSUB": "IDSUB",
    "AUMEL": "AUMEL",
    "AUSYD": "AUSYD",
    "THBKK": "THBKK",
    "THLCH": "THLCH",
    # New port LOCODE maps requested
    "CASHV": "KHKOS",
    "KHKOS": "KHKOS",
    "MYPEN": "MYPEN",
    "MYPGU": "MYPGU",
    "MYTPP": "MYTPP",
    "CNTAO": "CNTAO",
    "TWTXG": "TWTXG",
    "VNVUT": "VNVUT",
    "INMAA": "INMAA",
    "AEJEA": "AEJEA",
    "OMSOH": "OMSOH",
    "EGSOK": "EGSOK",
    "EGALY": "EGALY",
    "IDSRG": "IDSRG",
    "THLKR": "THLKR",
    "KNPNH": "KNPNH",
    "YEADE": "YEADE",
    "CNXMN": "CNXMN",
}

PORT_NAME_KEYWORD_MAP = {
    "port klang": "MYPKG",
    "klang": "MYPKG",
    "kaohsiung": "TWKHH",
    "keelung": "TWKEL",
    "keelung port": "TWKEL",
    "shanghai": "CNSHA",
    "shenzhen": "CNSZX",
    "ningbo": "CNNGB",
    "ho chi minh": "VNSGN",
    "ho chi minh city": "VNSGN",
    "hai phong": "VNHPH",
    "haiphong": "VNHPH",
    "karachi": "PKKHI",
    "nhava sheva": "INNSA",
    "jeddah": "SAJED",
    "ain sukhna": "EGAIS",
    "ainsukhna": "EGAIS",
    "sukhna": "EGAIS",
    "jakarta": "IDJKT",
    "batam": "IDBTM",
    "surabaya": "IDSUB",
    "melbourne": "AUMEL",
    "sydney": "AUSYD",
    "bangkok": "THBKK",
    "bangkok pat": "THBKK",
    "laem chabang": "THLCH",
    "laemchabang": "THLCH",
    # New port searchable keywords requested
    "sihanoukville": "KHKOS",
    "penang": "MYPEN",
    "pasir gudang": "MYPGU",
    "tanjung pelepas": "MYTPP",
    "qingdao": "CNTAO",
    "taichung": "TWTXG",
    "vung tau": "VNVUT",
    "chennai": "INMAA",
    "madras": "INMAA",
    "jebel ali": "AEJEA",
    "sohar": "OMSOH",
    "sokhna": "EGSOK",
    "alexandria": "EGALY",
    "semarang": "IDSRG",
    "lat krabang": "THLKR",
    "latkrabang": "THLKR",
    "phnom penh": "KNPNH",
    "aden": "YEADE",
    "xiamen": "CNXMN",
}


COUNTRY_CODE_TO_NAME = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AG": "Antigua and Barbuda",
    "AI": "Anguilla",
    "AL": "Albania",
    "AM": "Armenia",
    "AO": "Angola",
    "AQ": "Antarctica",
    "AR": "Argentina",
    "AS": "American Samoa",
    "AT": "Austria",
    "AU": "Australia",
    "AW": "Aruba",
    "AX": "Åland Islands",
    "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina",
    "BB": "Barbados",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BF": "Burkina Faso",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BI": "Burundi",
    "BJ": "Benin",
    "BL": "Saint Barthélemy",
    "BM": "Bermuda",
    "BN": "Brunei",
    "BO": "Bolivia",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BR": "Brazil",
    "BS": "Bahamas",
    "BT": "Bhutan",
    "BV": "Bouvet Island",
    "BW": "Botswana",
    "BY": "Belarus",
    "BZ": "Belize",
    "CA": "Canada",
    "CC": "Cocos (Keeling) Islands",
    "CD": "Democratic Republic of the Congo",
    "CF": "Central African Republic",
    "CG": "Republic of the Congo",
    "CH": "Switzerland",
    "CI": "Ivory Coast",
    "CK": "Cook Islands",
    "CL": "Chile",
    "CM": "Cameroon",
    "CN": "China",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CV": "Cape Verde",
    "CW": "Curaçao",
    "CX": "Christmas Island",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DK": "Denmark",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "EH": "Western Sahara",
    "ER": "Eritrea",
    "ES": "Spain",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FK": "Falkland Islands",
    "FM": "Micronesia",
    "FO": "Faroe Islands",
    "FR": "France",
    "GA": "Gabon",
    "GB": "United Kingdom",
    "GD": "Grenada",
    "GE": "Georgia",
    "GF": "French Guiana",
    "GG": "Guernsey",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GL": "Greenland",
    "GM": "Gambia",
    "GN": "Guinea",
    "GP": "Guadeloupe",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GS": "South Georgia and the South Sandwich Islands",
    "GT": "Guatemala",
    "GU": "Guam",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HK": "Hong Kong",
    "HM": "Heard Island and McDonald Islands",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IM": "Isle of Man",
    "IN": "India",
    "IO": "British Indian Ocean Territory",
    "IQ": "Iraq",
    "IR": "Iran",
    "IS": "Iceland",
    "IT": "Italy",
    "JE": "Jersey",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KM": "Comoros",
    "KN": "Saint Kitts and Nevis",
    "KP": "North Korea",
    "KR": "South Korea",
    "KW": "Kuwait",
    "KY": "Cayman Islands",
    "KZ": "Kazakhstan",
    "LA": "Laos",
    "LB": "Lebanon",
    "LC": "Saint Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LR": "Liberia",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "LY": "Libya",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova",
    "ME": "Montenegro",
    "MF": "Saint Martin",
    "MG": "Madagascar",
    "MH": "Marshall Islands",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MM": "Myanmar",
    "MN": "Mongolia",
    "MO": "Macau",
    "MP": "Northern Mariana Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MS": "Montserrat",
    "MT": "Malta",
    "MU": "Mauritius",
    "MV": "Maldives",
    "MW": "Malawi",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NC": "New Caledonia",
    "NE": "Niger",
    "NF": "Norfolk Island",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NU": "Niue",
    "NZ": "New Zealand",
    "OM": "Oman",
    "PA": "Panama",
    "PE": "Peru",
    "PF": "French Polynesia",
    "PG": "Papua New Guinea",
    "PH": "Philippines",
    "PK": "Pakistan",
    "PL": "Poland",
    "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn",
    "PR": "Puerto Rico",
    "PS": "Palestine",
    "PT": "Portugal",
    "PW": "Palau",
    "PY": "Paraguay",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RS": "Serbia",
    "RU": "Russia",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SB": "Solomon Islands",
    "SC": "Seychelles",
    "SD": "Sudan",
    "SE": "Sweden",
    "SG": "Singapore",
    "SH": "Saint Helena",
    "SI": "Slovenia",
    "SJ": "Svalbard and Jan Mayen",
    "SK": "Slovakia",
    "SL": "Sierra Leone",
    "SM": "San Marino",
    "SN": "Senegal",
    "SO": "Somalia",
    "SR": "Suriname",
    "SS": "South Sudan",
    "ST": "São Tomé and Príncipe",
    "SV": "El Salvador",
    "SX": "Sint Maarten",
    "SY": "Syria",
    "SZ": "Eswatini",
    "TC": "Turks and Caicos Islands",
    "TD": "Chad",
    "TF": "French Southern Territories",
    "TG": "Togo",
    "TH": "Thailand",
    "TJ": "Tajikistan",
    "TK": "Tokelau",
    "TL": "East Timor",
    "TM": "Turkmenistan",
    "TN": "Tunisia",
    "TO": "Tonga",
    "TR": "Turkey",
    "TT": "Trinidad and Tobago",
    "TV": "Tuvalu",
    "TW": "Taiwan",
    "TZ": "Tanzania",
    "UA": "Ukraine",
    "UG": "Uganda",
    "UM": "United States Minor Outlying Islands",
    "US": "United States",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VA": "Vatican City",
    "VC": "Saint Vincent and the Grenadines",
    "VE": "Venezuela",
    "VG": "British Virgin Islands",
    "VI": "U.S. Virgin Islands",
    "VN": "Vietnam",
    "VU": "Vanuatu",
    "WF": "Wallis and Futuna",
    "WS": "Samoa",
    "XK": "Kosovo",
    "YE": "Yemen",
    "YT": "Mayotte",
    "ZA": "South Africa",
    "ZM": "Zambia",
    "ZW": "Zimbabwe"
}

DEFAULT_POPULAR_PORTS = {
    "GBBEL", "NLRTM", "SGSIN", "DEHAM", "CNSHA", "CNTAO", "CNSZX", "CNNGB", "AEJEA", "VNHPH",
    "VNSGN", "PKKHI", "INNSA", "SAJED", "EGAIS", "EGALX", "EGALY", "IDJKT", "IDBTM", "IDSUB",
    "AUMEL", "AUSYD", "THBKK", "THLCH", "USLAX", "USLGB", "USNYC", "USOAK", "USSAV", "GBFXT",
    "GBLGP", "GBSOU", "FRFOS", "FRLEH", "ESBCN", "ESALG", "ESVLC", "ITGOA", "ITSPE", "BEZEE",
    "BEANR", "PLGDN", "GRPIR", "TRMER", "TRIST", "KRPUS", "JPTYO", "JPYOK", "JPOSK", "JPUKB",
    "JPHKT", "TWKHH", "TWKEL", "TWTXG", "MYPKG", "MYLPK", "MYPEN", "MYPGU", "MYTPP", "LKCMB",
    "BDCGP", "EGSOK", "OMSOH", "YEADE", "KHKOS", "KNPNH", "TLDIL", "INMAA", "IDSRG", "THLKR",
    "VNVUT", "CNXMN"
}

class PortManager:
    _instance = None
    _ports = {}
    _aliases = {}
    _carrier_ports_cache = {}

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

        # Load persistent carrier ports cache
        cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "carrier_ports_cache.json")
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self._carrier_ports_cache = json.load(f)
            else:
                self._carrier_ports_cache = {}
        except Exception as e:
            print(f"Error loading carrier ports cache: {e}")
            self._carrier_ports_cache = {}

        # Load dynamic popular ports and boosted countries config
        self.popular_ports = set(DEFAULT_POPULAR_PORTS)
        self.boosted_countries = set()
        
        config_path = os.path.join(os.path.dirname(__file__), "..", "data", "popular_ports_config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "popular_ports" in config:
                        self.popular_ports = {p.upper().strip() for p in config["popular_ports"] if p.strip()}
                    if "boosted_countries" in config:
                        self.boosted_countries = {c.upper().strip() for c in config["boosted_countries"] if c.strip()}
            else:
                self._save_config()
        except Exception as e:
            print(f"Error loading popular ports config: {e}")

    def _save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "data", "popular_ports_config.json")
        config = {
            "popular_ports": sorted(list(self.popular_ports)),
            "boosted_countries": sorted(list(self.boosted_countries))
        }
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving popular ports config: {e}")

    def update_popular_ports_config(self, popular_ports: List[str], boosted_countries: List[str]):
        # Validate and filter codes
        valid_ports = set()
        for p in popular_ports:
            p_clean = p.strip().upper()
            if len(p_clean) == 5 and p_clean in self._ports:
                valid_ports.add(p_clean)
                
        valid_countries = set()
        for c in boosted_countries:
            c_clean = c.strip().upper()
            if c_clean in COUNTRY_CODE_TO_NAME:
                valid_countries.add(c_clean)
                
        self.popular_ports = valid_ports
        self.boosted_countries = valid_countries
        self._save_config()

    def get_popular_ports_config(self) -> Dict[str, List[str]]:
        return {
            "popular_ports": sorted(list(self.popular_ports)),
            "boosted_countries": sorted(list(self.boosted_countries))
        }

    def get_cached_carrier_port(self, carrier: str, locode: str) -> Optional[str]:
        """Retrieve verified carrier port name from persistent cache by UN/LOCODE."""
        carrier_key = carrier.strip().lower()
        locode_key = locode.strip().upper()
        return self._carrier_ports_cache.get(carrier_key, {}).get(locode_key)

    def set_cached_carrier_port(self, carrier: str, locode: str, exact_name: str) -> None:
        """Cache verified carrier port name and save persistently to carrier_ports_cache.json."""
        if not locode or not exact_name:
            return
        carrier_key = carrier.strip().lower()
        locode_key = locode.strip().upper()
        
        # Normalize: collapse all whitespace/newlines into single spaces and strip
        import re as _re
        exact_name = _re.sub(r'[\r\n]+', ' ', exact_name)
        exact_name = _re.sub(r'  +', ' ', exact_name).strip()
        if not exact_name:
            return
        
        # Reject garbage values that are clearly not port/location names
        GARBAGE_KEYWORDS = [
            "continue to book", "close", "sign in", "log in", "accept", "cookie",
            "subscribe", "submit", "cancel", "no results", "no matching", "loading",
            "check your spelling", "english spelling", "full city name", "abbreviation",
            "location matching", "try using", "no location", "please enter",
            "select container", "select commodity", "price owner",
        ]
        name_lower = exact_name.lower()
        if any(kw in name_lower for kw in GARBAGE_KEYWORDS):
            print(f"[PORT CACHE] Rejected garbage value for {carrier.upper()}: {locode_key} -> '{exact_name}'")
            return
        
        if carrier_key not in self._carrier_ports_cache:
            self._carrier_ports_cache[carrier_key] = {}
            
        # Only write and save if it's a new or updated mapping
        if self._carrier_ports_cache[carrier_key].get(locode_key) != exact_name:
            self._carrier_ports_cache[carrier_key][locode_key] = exact_name
            
            cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "carrier_ports_cache.json")
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self._carrier_ports_cache, f, indent=2)
                print(f"[PORT CACHE] Saved mapping for {carrier.upper()}: {locode_key} -> '{exact_name}'")
            except Exception as e:
                print(f"[PORT CACHE] Failed to write cache file: {e}")

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
        port = self._ports.get(code.upper())
        if port:
            port_copy = dict(port)
            country_code = port_copy.get('country', '').upper()
            port_copy['country_name'] = COUNTRY_CODE_TO_NAME.get(country_code, country_code)
            return port_copy
        return None

    def search_port(self, query: str, country: Optional[str] = None) -> List[Dict]:
        """
        Search for ports by code, name, or alias.
        Returns top matches ranked by relevance.
        """
        query = query.strip()
        if not query:
            return []

        query_raw = re.sub(r'\s+', ' ', query.lower()).strip()
        query_norm = self.normalize_port_input(query)
        
        # If query_norm is empty, fallback to query_raw
        if not query_norm:
            query_norm = query_raw

        results = []
        seen_codes = set()

        # Helper to clean parenthesized names (e.g. "Port Klang (Pelabuhan Klang)" -> "port klang")
        def get_clean_name(name_str):
            if not name_str:
                return ""
            return re.sub(r'\s*\([^)]*\)', '', name_str).lower().strip()

        # 1. Exact full code match
        direct_match = self.get_port_by_code(query.upper())
        if direct_match:
            if not country or direct_match['country'].upper() == country.upper():
                results.append((direct_match, 0.0)) # Rank 0 (top)
                seen_codes.add(direct_match['code'])

        # We will collect candidates and compute their best score
        candidates = {} # code -> (port, best_score)

        def add_candidate(port, score):
            code = port['code']
            if country and port['country'].upper() != country.upper():
                return
            if code in seen_codes:
                return
            if code in candidates:
                # Keep the lower (better) score
                candidates[code] = (port, min(candidates[code][1], score))
            else:
                candidates[code] = (port, score)

        # 2. Check exact, prefix, and substring matches on all ports
        for code, port in self._ports.items():
            if code in seen_codes:
                continue

            name_lower = port['name'].lower()
            name_ascii_lower = port.get('name_ascii', '').lower()
            clean_name = get_clean_name(port['name'])
            clean_name_ascii = get_clean_name(port.get('name_ascii', ''))

            # Exact matches (Score 1.0)
            if (query_raw == name_lower or 
                query_raw == name_ascii_lower or 
                query_raw == clean_name or 
                query_raw == clean_name_ascii or
                query_norm == name_lower or
                query_norm == name_ascii_lower or
                query_norm == clean_name or
                query_norm == clean_name_ascii):
                add_candidate(port, 1.0)
                continue

            # Prefix matches on raw query (Score 1.2)
            if (name_lower.startswith(query_raw) or 
                name_ascii_lower.startswith(query_raw) or 
                clean_name.startswith(query_raw) or 
                clean_name_ascii.startswith(query_raw)):
                add_candidate(port, 1.2)
                continue

            # Prefix matches on normalized query (Score 1.5)
            if (name_lower.startswith(query_norm) or 
                name_ascii_lower.startswith(query_norm) or 
                clean_name.startswith(query_norm) or 
                clean_name_ascii.startswith(query_norm)):
                add_candidate(port, 1.5)
                continue

            # Substring matches on raw query (Score 1.8)
            if (query_raw in name_lower or 
                query_raw in name_ascii_lower or 
                query_raw in clean_name or 
                query_raw in clean_name_ascii):
                add_candidate(port, 1.8)
                continue

            # Substring matches on normalized query (Score 2.0)
            if (query_norm in name_lower or 
                query_norm in name_ascii_lower or 
                query_norm in clean_name or 
                query_norm in clean_name_ascii):
                add_candidate(port, 2.0)
                continue

        # 3. Check alias exact, prefix, and substring matches
        for alias_key, codes in self._aliases.items():
            alias_lower = alias_key.lower()
            for code in codes:
                if code in seen_codes:
                    continue
                port = self._ports.get(code)
                if not port:
                    continue

                if query_raw == alias_lower or query_norm == alias_lower:
                    add_candidate(port, 1.0)
                elif alias_lower.startswith(query_raw):
                    add_candidate(port, 1.3)
                elif alias_lower.startswith(query_norm):
                    add_candidate(port, 1.6)
                elif query_raw in alias_lower:
                    add_candidate(port, 1.9)
                elif query_norm in alias_lower:
                    add_candidate(port, 2.1)

        # Convert candidates to list of results
        for port, score in candidates.values():
            port_copy = dict(port)
            country_code = port_copy.get('country', '').upper()
            port_copy['country_name'] = COUNTRY_CODE_TO_NAME.get(country_code, country_code)
            results.append((port_copy, score))
            seen_codes.add(port['code'])

        # 4. Fuzzy match on alias keys if we don't have enough results (Score 3.0)
        if len(results) < 10:
            alias_keys = list(self._aliases.keys())
            close_aliases = get_close_matches(query_norm, alias_keys, n=10, cutoff=0.7)
            for alias in close_aliases:
                for code in self._aliases[alias]:
                    if code not in seen_codes:
                        port = self._ports.get(code)
                        if port:
                            if country and port['country'].upper() != country.upper():
                                continue
                            port_copy = dict(port)
                            country_code = port_copy.get('country', '').upper()
                            port_copy['country_name'] = COUNTRY_CODE_TO_NAME.get(country_code, country_code)
                            results.append((port_copy, 3.0))
                            seen_codes.add(code)

        # Sorting logic:
        # Rank by score (lower is better), then by is_popular, then by is_boosted_country, then by status confidence, then by length of name
        def ranking_key(item):
            port, score = item
            is_popular = 0 if port['code'] in self.popular_ports else 1
            is_boosted_country = 0 if port['country'] in self.boosted_countries else 1
            
            # Status confidence: AI/AF > RL > others
            status = port.get('status', '')
            if status in ('AI', 'AF'):
                status_score = 0
            elif status == 'RL':
                status_score = 1
            else:
                status_score = 2
                
            return (score, is_popular, is_boosted_country, status_score, len(port['name']), port['name'])

        results.sort(key=ranking_key)
        return [r[0] for r in results]

    def suggest_ports(self, query: str, limit: int = 5) -> List[Dict]:
        """Suggest top N ports for a partial query."""
        results = self.search_port(query)
        return results[:limit]

    def resolve_port_for_carrier(self, text: str, carrier: str) -> str:
        """
        Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')
        to the exact spelling required by the target carrier (e.g., 'Haiphong' for Maersk,
        'Hai Phong' for ONE).
        """
        if not text:
            return ""

        carrier_key = carrier.strip().lower()

        text_lower = text.lower().strip()
        if "rotterdam" in text_lower or text_lower == "nlrtm":
            if carrier_key in ("maersk", "msc"):
                return "Rotterdam"
            else:
                return "NLRTM"

        # Rule for GreenX and MSC: autocomplete field accepts the raw LOCODE (e.g. SGSIN, DEHAM)
        if carrier_key in ("greenx", "msc"):
            # Extract LOCODE from input text
            extracted_locode = None
            paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
            if paren_match:
                extracted_locode = (paren_match.group(1) + paren_match.group(2)).upper()
            else:
                word_match = re.search(r'\b([A-Za-z]{2})\s*([A-Za-z]{3})\b', text)
                if word_match:
                    candidate = (word_match.group(1) + word_match.group(2)).upper()
                    if candidate in self._ports:
                        extracted_locode = candidate
            if not extracted_locode:
                clean_word = text.strip()
                if len(clean_word) == 5 and clean_word.isalpha():
                    candidate = clean_word.upper()
                    if candidate in self._ports:
                        extracted_locode = candidate
            if not extracted_locode:
                # Try keyword lookup to get the LOCODE
                clean_text = re.sub(r'\s*\([^)]*\)', '', text).strip()
                norm_text_clean = re.sub(r'\b(port|of|terminal|container)\b', '', clean_text.lower())
                norm_text_clean = re.sub(r'\s+', ' ', norm_text_clean).strip()
                for keyword, locode in PORT_NAME_KEYWORD_MAP.items():
                    if keyword == norm_text_clean or keyword == clean_text.lower():
                        extracted_locode = locode
                        break
            if not extracted_locode:
                # Try database search fallback
                results = self.search_port(text)
                if results:
                    extracted_locode = results[0]['code'].upper()
            # Return the LOCODE itself — GreenX and MSC autocomplete search by LOCODE
            if extracted_locode and extracted_locode in self._ports:
                return extracted_locode
            # Fallback: return whatever was passed in (already a LOCODE)
            return text.strip().upper()

        # Rule for Maersk: Follow the user's exact text string, but resolve LOCODEs and keywords to port names
        if carrier_key == "maersk":
            clean_text = re.sub(r'\s*\([^)]*\)', '', text).strip()
            
            # Check if there is an extracted LOCODE in the input
            extracted_locode = None
            paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
            if paren_match:
                extracted_locode = (paren_match.group(1) + paren_match.group(2)).upper()
            else:
                word_match = re.search(r'\b([A-Za-z]{2})\s*([A-Za-z]{3})\b', text)
                if word_match:
                    candidate = (word_match.group(1) + word_match.group(2)).upper()
                    if candidate in self._ports:
                        extracted_locode = candidate
            
            if not extracted_locode:
                clean_word = text.strip()
                if len(clean_word) == 5 and clean_word.isalpha():
                    candidate = clean_word.upper()
                    if candidate in self._ports:
                        extracted_locode = candidate
            
            # Check if clean_text is a commonly used keyword
            if not extracted_locode:
                norm_text_clean = re.sub(r'\b(port|of|terminal|container)\b', '', clean_text.lower())
                norm_text_clean = re.sub(r'\s+', ' ', norm_text_clean).strip()
                for keyword, locode in PORT_NAME_KEYWORD_MAP.items():
                    if keyword == norm_text_clean or keyword == clean_text.lower():
                        extracted_locode = locode
                        break

            # If a LOCODE was resolved, translate it to carrier's preferred name or database name
            if extracted_locode:
                overrides = CARRIER_PORT_OVERRIDES.get(carrier_key, {})
                if extracted_locode in overrides:
                    return overrides[extracted_locode]
                
                port_data = self.get_port_by_code(extracted_locode)
                if port_data:
                    return port_data["name"]
            
            return clean_text

        # Rule for CMA, ONE, and Hapag-Lloyd: Auto-translate to their PORT CODE (LOCODE)
        if carrier_key in ("cma", "one", "hapag"):
            # A. Try matching commonly used port name keywords first
            norm_text = text.lower().strip()
            norm_text_clean = re.sub(r'\b(port|of|terminal|container)\b', '', norm_text)
            norm_text_clean = re.sub(r'\s+', ' ', norm_text_clean).strip()

            target_locode = None
            for keyword, locode in PORT_NAME_KEYWORD_MAP.items():
                if keyword == norm_text_clean or keyword == norm_text:
                    target_locode = locode
                    break

            # B. If not found, try to extract a 5-letter code from parentheses or direct code
            if not target_locode:
                locode_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
                if locode_match:
                    extracted = (locode_match.group(1) + locode_match.group(2)).upper()
                    if extracted in PORT_MAP_CMA_ONE:
                        target_locode = PORT_MAP_CMA_ONE[extracted]
                else:
                    clean_word = text.strip()
                    if len(clean_word) == 5 and clean_word.isalpha():
                        extracted = clean_word.upper()
                        if extracted in PORT_MAP_CMA_ONE:
                            target_locode = PORT_MAP_CMA_ONE[extracted]

            # C. If still not found, search in our ports database to see if the first search result is one of the commonly used ports
            if not target_locode:
                results = self.search_port(text)
                if results:
                    first_code = results[0]['code'].upper()
                    if first_code in PORT_MAP_CMA_ONE:
                        target_locode = PORT_MAP_CMA_ONE[first_code]

            # D. If we matched a target commonly used port:
            if target_locode:
                # ONE special override: Ain Sukhna (EGAIS) -> Alexandria (EGALY)
                if carrier_key == "one" and target_locode == "EGAIS":
                    return "EGALY"
                # CMA special override: Sokhna (EGSOK) -> Ain Sukhna (EGAIS)
                if carrier_key == "cma" and target_locode == "EGSOK":
                    return "EGAIS"
                # Sihanoukville override: CASHV -> KHKOS
                if target_locode == "CASHV":
                    return "KHKOS"
                return target_locode

            # E. Fallback: For CMA/ONE, also resolve any other valid port in the database to its standard LOCODE
            extracted_locode = None
            paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
            if paren_match:
                extracted_locode = (paren_match.group(1) + paren_match.group(2)).upper()
            else:
                word_match = re.search(r'\b([A-Za-z]{2})\s*([A-Za-z]{3})\b', text)
                if word_match:
                    candidate = (word_match.group(1) + word_match.group(2)).upper()
                    if candidate in self._ports:
                        extracted_locode = candidate

            if not extracted_locode:
                clean_word = text.strip()
                if len(clean_word) == 5 and clean_word.isalpha():
                    candidate = clean_word.upper()
                    if candidate in self._ports:
                        extracted_locode = candidate

            if not extracted_locode or extracted_locode not in self._ports:
                results = self.search_port(text)
                if results:
                    extracted_locode = results[0]['code']

            if extracted_locode and extracted_locode in self._ports:
                # ONE special override: Ain Sukhna (EGAIS) -> Alexandria (EGALY)
                if carrier_key == "one" and extracted_locode == "EGAIS":
                    return "EGALY"
                # CMA special override: Sokhna (EGSOK) -> Ain Sukhna (EGAIS)
                if carrier_key == "cma" and extracted_locode == "EGSOK":
                    return "EGAIS"
                # Sihanoukville override: CASHV -> KHKOS
                if extracted_locode == "CASHV":
                    return "KHKOS"
                return extracted_locode

        # Ultimate fallback: clean up parentheses from the input text
        clean_text = re.sub(r'\s*\([^)]*\)', '', text)
        return clean_text.strip()


    def get_carrier_search_query(self, original_input: str, resolved_name: str) -> str:
        """
        Constructs the specific search query to type into carrier search boxes.
        If the original input has a LOCODE or country, appends the country to narrow results.
        E.g. original_input='Casablanca (MACAS)' -> 'Casablanca, Morocco'
        """
        if not original_input:
            return resolved_name

        # 1. Try to extract LOCODE
        paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', original_input)
        locode = None
        if paren_match:
            locode = (paren_match.group(1) + paren_match.group(2)).upper()
        else:
            # Check if 5-letter word is at the end or boundary
            clean = original_input.strip()
            if len(clean) == 5 and clean.isalpha():
                locode = clean.upper()

        country_name = None
        if locode:
            port_obj = self.get_port_by_code(locode)
            if port_obj:
                country_code = port_obj.get("country", "").upper()
                country_name = COUNTRY_CODE_TO_NAME.get(country_code)

        # 2. If no locode or port_obj, try to extract country name from comma format
        if not country_name:
            parts = original_input.split(',')
            if len(parts) > 1:
                c_part = parts[-1].strip()
                c_part = re.sub(r'\s*\([^)]*\)', '', c_part).strip()
                if c_part:
                    country_name = c_part

        # 3. Append country name if found and not already in resolved_name
        if country_name and country_name.lower() not in resolved_name.lower():
            return f"{resolved_name}, {country_name}"

        return resolved_name

# Convenience functions
def get_port_by_code(code: str):
    return PortManager().get_port_by_code(code)

def search_port(query: str, country: str = None):
    return PortManager().search_port(query, country)

def normalize_port_input(text: str):
    return PortManager().normalize_port_input(text)

def suggest_ports(query: str, limit: int = 5):
    return PortManager().suggest_ports(query, limit)

def resolve_port_for_carrier(text: str, carrier: str):
    return PortManager().resolve_port_for_carrier(text, carrier)

def get_carrier_search_query(original_input: str, resolved_name: str):
    return PortManager().get_carrier_search_query(original_input, resolved_name)

def get_cached_carrier_port(carrier: str, locode: str):
    return PortManager().get_cached_carrier_port(carrier, locode)

def set_cached_carrier_port(carrier: str, locode: str, exact_name: str):
    return PortManager().set_cached_carrier_port(carrier, locode, exact_name)

def get_popular_ports_config():
    return PortManager().get_popular_ports_config()

def update_popular_ports_config(popular_ports: List[str], boosted_countries: List[str]):
    return PortManager().update_popular_ports_config(popular_ports, boosted_countries)
