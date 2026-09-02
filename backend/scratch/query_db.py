import sqlite3
import json

conn = sqlite3.connect("infreight.db")
cursor = conn.cursor()

# Get the latest rate search
cursor.execute("SELECT id, origin, destination, container_type, selected_carriers, status, created_at FROM rate_searches ORDER BY created_at DESC LIMIT 1")
row = cursor.fetchone()

if row:
    search_id, origin, destination, container_type, selected_carriers, status, created_at = row
    print("="*80)
    print(f"LATEST RATE SEARCH: {search_id}")
    print(f"Origin: {origin} -> Destination: {destination}")
    print(f"Container Type: {container_type}")
    print(f"Selected Carriers: {selected_carriers}")
    print(f"Status: {status}")
    print(f"Created At: {created_at}")
    print("="*80)
    
    # Get the carrier search results
    cursor.execute("SELECT carrier, status, error_message, started_at, completed_at FROM carrier_search_results WHERE search_id = ?", (search_id,))
    results = cursor.fetchall()
    
    for res in results:
        carrier, status, error_msg, started_at, completed_at = res
        print(f"CARRIER: {carrier}")
        print(f"  Status: {status}")
        print(f"  Started: {started_at} | Completed: {completed_at}")
        print(f"  Error Message: {error_msg}")
        print("-" * 50)
else:
    print("No rate searches found in database.")

conn.close()
