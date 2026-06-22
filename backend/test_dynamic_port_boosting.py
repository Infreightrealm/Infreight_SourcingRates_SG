import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.port_manager import PortManager, search_port, get_popular_ports_config, update_popular_ports_config

def test_dynamic_boosting():
    print("=== Testing Dynamic Port Boosting ===")
    
    # 1. Fetch current config
    original_config = get_popular_ports_config()
    print("Original config loaded successfully.")
    
    try:
        # 2. Check initial search for 'belfast'
        # GBBEL should be first because it is in the default popular ports
        results = search_port("belfast")
        initial_first = results[0]['code']
        print(f"Initial search for 'belfast' top result: {initial_first} ({results[0]['name']}, status: {results[0]['status']})")
        assert initial_first == "GBBEL", f"Expected GBBEL initially, got {initial_first}"
        
        # 3. Clear popular ports list
        print("Clearing popular ports config...")
        update_popular_ports_config(popular_ports=[], boosted_countries=[])
        
        # 4. Search again - GBBEL status is 'AF' (status_score 0) while DMBEL is 'RL' (status_score 1),
        # so GBBEL will still rank first based on status confidence.
        results_after_clear = search_port("belfast")
        cleared_first = results_after_clear[0]['code']
        print(f"Search for 'belfast' after config clear: {cleared_first} ({results_after_clear[0]['name']}, status: {results_after_clear[0]['status']})")
        assert cleared_first == "GBBEL", f"Expected GBBEL to still be first due to status confidence, got {cleared_first}"
        
        # 5. Boost DMBEL by adding it to popular ports config
        print("Boosting DMBEL by adding it to popular ports config...")
        update_popular_ports_config(popular_ports=["DMBEL"], boosted_countries=[])
        
        # 6. Search again - DMBEL should override status confidence and rank first
        results_after_dm_boost = search_port("belfast")
        dm_boosted_first = results_after_dm_boost[0]['code']
        print(f"Search for 'belfast' after boosting DMBEL: {dm_boosted_first} ({results_after_dm_boost[0]['name']}, status: {results_after_dm_boost[0]['status']})")
        assert dm_boosted_first == "DMBEL", f"Expected DMBEL to rank first under popular ports boost, got {dm_boosted_first}"

        # 7. Add GBBEL back to popular ports config
        print("Adding GBBEL back to popular ports config...")
        update_popular_ports_config(popular_ports=["GBBEL"], boosted_countries=[])
        
        # 8. Search again - GBBEL should rank first again
        results_after_add = search_port("belfast")
        added_first = results_after_add[0]['code']
        print(f"Search for 'belfast' after adding GBBEL: {added_first} ({results_after_add[0]['name']}, status: {results_after_add[0]['status']})")
        assert added_first == "GBBEL", f"Expected GBBEL to rank first again, got {added_first}"

        # 7. Test country boost - boost 'SV' (El Salvador)
        print("Boosting country 'SV' (El Salvador)...")
        update_popular_ports_config(popular_ports=[], boosted_countries=["SV"])
        
        results_country_boost = search_port("belfast")
        boosted_first = results_country_boost[0]['code']
        print(f"Search for 'belfast' after boosting country SV: {boosted_first} ({results_country_boost[0]['name']}, country: {results_country_boost[0]['country']})")
        assert boosted_first == "SVBEL", f"Expected SVBEL to rank first under SV country boost, got {boosted_first}"

        print("=== ALL DYNAMIC BOOSTING TESTS PASSED ===")
        
    finally:
        # Restore original config
        print("Restoring original configuration...")
        update_popular_ports_config(
            popular_ports=original_config["popular_ports"],
            boosted_countries=original_config["boosted_countries"]
        )

if __name__ == "__main__":
    test_dynamic_boosting()
