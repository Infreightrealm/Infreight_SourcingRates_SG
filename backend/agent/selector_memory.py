"""
Selector Memory — stores and retrieves human-approved selector patches.
"""
import os
import json
import datetime

MEMORY_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "selector_memory.json"
)

def _load_memory() -> dict:
    """Loads memory JSON file. Returns empty dict if file is missing or invalid."""
    if not os.path.exists(MEMORY_FILE_PATH):
        # Create directory if missing
        os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)
        return {}
    try:
        with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Selector Memory] Error loading memory file: {e}")
        return {}

def _save_memory(memory: dict):
    """Saves memory dict back to JSON file."""
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4)
    except Exception as e:
        print(f"[Selector Memory] Error writing memory file: {e}")

def get_approved_selector(carrier: str, step_name: str, original_selector: str) -> str | None:
    """
    Looks up if there is an approved replacement selector for the given carrier and step.
    """
    carrier_key = carrier.upper()
    memory = _load_memory()
    
    carrier_data = memory.get(carrier_key, {})
    step_data = carrier_data.get(step_name, {})
    
    # Check if the entry is valid and approved
    if step_data.get("status") == "APPROVED":
        approved = step_data.get("approved_selector")
        print(f"[Selector Memory] Found approved replacement selector for {carrier_key}:{step_name} -> '{approved}'")
        return approved
        
    return None

def save_approved_selector(carrier: str, step_name: str, original_selector: str, approved_selector: str):
    """
    Stores an approved replacement selector.
    """
    carrier_key = carrier.upper()
    memory = _load_memory()
    
    if carrier_key not in memory:
        memory[carrier_key] = {}
        
    memory[carrier_key][step_name] = {
        "original_selector": original_selector,
        "approved_selector": approved_selector,
        "status": "APPROVED",
        "approved_at": datetime.datetime.now().isoformat(),
        "confidence": "HIGH"
    }
    
    _save_memory(memory)
    print(f"[Selector Memory] Successfully saved approved selector for {carrier_key}:{step_name} -> '{approved_selector}'")

def reject_selector(carrier: str, step_name: str):
    """
    Marks any proposed selector for this step as REJECTED.
    """
    carrier_key = carrier.upper()
    memory = _load_memory()
    
    if carrier_key in memory and step_name in memory[carrier_key]:
        memory[carrier_key][step_name]["status"] = "REJECTED"
        memory[carrier_key][step_name]["rejected_at"] = datetime.datetime.now().isoformat()
        _save_memory(memory)
        print(f"[Selector Memory] Marked selector for {carrier_key}:{step_name} as REJECTED")
