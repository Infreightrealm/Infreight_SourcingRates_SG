import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from services.job_service import _detect_port_mismatch
from services.port_manager import get_carrier_overrides

res = _detect_port_mismatch("San Juan", "PRSJU", "San Juan, Puerto Rico")
print(f"_detect_port_mismatch('San Juan', 'PRSJU', 'San Juan, Puerto Rico') -> {res}")

overrides = get_carrier_overrides("maersk")
print(f"Maersk Overrides: {overrides}")
