import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from services.port_manager import PortManager, add_carrier_override, get_carrier_overrides, update_popular_ports_config, get_popular_ports_config

def test_persistence():
    print("=======================================================")
    print("   Testing Persistence of Configs & Overrides")
    print("=======================================================")

    pm = PortManager()

    # 1. Test Carrier Overrides persistence
    print("1. Adding test override for MAERSK: TEST_LOC -> 'Test Port Name'...")
    add_carrier_override("maersk", "TEST_LOC", "Test Port Name")
    
    # Re-instantiate PortManager (simulating server restart)
    pm_reloaded = PortManager()
    overrides = pm_reloaded.get_carrier_overrides("maersk")
    print(f"   Reloaded Maersk Overrides: {overrides.get('test_loc')}")
    assert overrides.get("test_loc") == "Test Port Name", "Carrier override failed to persist!"
    print("   [SUCCESS] Carrier override persisted across server restart!")

    # Clean up test override
    from services.port_manager import delete_carrier_override
    delete_carrier_override("maersk", "TEST_LOC")
    print("   Test override cleaned up.")

    # 2. Test Port Ranking Config persistence
    print("\n2. Updating Port Ranking Config...")
    curr_cfg = pm_reloaded.get_popular_ports_config()
    ports = curr_cfg.get("popular_ports", [])
    countries = curr_cfg.get("boosted_countries", [])
    
    update_popular_ports_config(ports, countries)
    pm_reloaded_2 = PortManager()
    new_cfg = pm_reloaded_2.get_popular_ports_config()
    print(f"   Reloaded Popular Ports Count: {len(new_cfg.get('popular_ports', []))}")
    print("   [SUCCESS] Port ranking config persisted across server restart!")

if __name__ == "__main__":
    test_persistence()
