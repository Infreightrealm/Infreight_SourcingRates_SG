from services.port_manager import search_port, get_port_by_code, suggest_ports, resolve_port_for_carrier

def test():
    print("Testing SGSIN...")
    p = get_port_by_code("SGSIN")
    print(p)
    
    print("\nSearching 'singapore'...")
    results = search_port("singapore")
    for r in results[:3]:
        print(f"Match: {r['code']} - {r['name']} ({r['status']})")
        
    print("\nSearching 'hamburg port'...")
    results = search_port("hamburg port")
    for r in results[:3]:
        print(f"Match: {r['code']} - {r['name']} ({r['status']})")

    print("\nSearching 'ho chi minh'...")
    results = search_port("ho chi minh")
    for r in results[:3]:
        print(f"Match: {r['code']} - {r['name']} ({r['status']})")

    print("\nSearching 'belfast'...")
    results = search_port("belfast")
    for r in results[:3]:
        print(f"Match: {r['code']} - {r['name']} ({r['status']}) - Country: {r.get('country_name')}")
    assert results[0]['code'] == 'GBBEL', f"Expected GBBEL to be first match for belfast, got {results[0]['code']}"

    print("\nTesting resolve_port_for_carrier...")
    test_cases = [
        ("VN HPH", "maersk", "VN HPH"),
        ("VN HPH", "one", "VNHPH"),
        ("Haiphong (VN HPH)", "maersk", "Haiphong"),
        ("Haiphong (VN HPH)", "one", "VNHPH"),
        ("Haiphong", "maersk", "Haiphong"),
        ("Haiphong", "one", "VNHPH"),
        ("Hai Phong", "maersk", "Hai Phong"),
        ("Hai Phong", "one", "VNHPH"),
        ("Ho Chi Minh City", "maersk", "Ho Chi Minh City"),
        ("Ho Chi Minh City", "one", "VNSGN"),
        ("VNSGN", "maersk", "VNSGN"),
        ("VNSGN", "one", "VNSGN"),
        ("Singapore (SGSIN)", "maersk", "Singapore"),
        ("Singapore (SGSIN)", "one", "SGSIN"),
        ("Ain Sukhna", "cma", "EGAIS"),
        ("Ain Sukhna", "one", "EGALY"),
        ("port klang", "maersk", "port klang"),
        ("port klang", "cma", "MYPKG"),
        ("port klang", "one", "MYPKG"),
        # Rotterdam overrides
        ("Rotterdam", "maersk", "Rotterdam"),
        ("Rotterdam", "msc", "Rotterdam"),
        ("Rotterdam", "one", "NLRTM"),
        ("Rotterdam", "cma", "NLRTM"),
        ("Rotterdam", "hapag", "NLRTM"),
        ("Rotterdam", "greenx", "NLRTM"),
        ("Rotterdam", "oocl", "NLRTM"),
        ("Rotterdam, Netherlands", "maersk", "Rotterdam"),
        ("Rotterdam, Netherlands", "one", "NLRTM"),
        ("nlrtm", "maersk", "Rotterdam"),
        ("nlrtm", "one", "NLRTM"),
    ]

    for q, carrier, expected in test_cases:
        resolved = resolve_port_for_carrier(q, carrier)
        success = resolved == expected
        print(f"[{'PASS' if success else 'FAIL'}] Input: '{q}' -> Carrier: {carrier} | Resolved: '{resolved}' | Expected: '{expected}'")

    print("\nTesting get_carrier_search_query...")
    query_cases = [
        ("Casablanca (MACAS)", "Casablanca", "Casablanca, Morocco"),
        ("Port Klang (MYPKG)", "Port Klang", "Port Klang, Malaysia"),
        ("Singapore (SGSIN)", "Singapore", "Singapore"),
        ("port klang", "Port Klang", "Port Klang"),
        ("Casablanca, Morocco", "Casablanca", "Casablanca, Morocco"),
        ("Casablanca, Chile (CLCAS)", "Casablanca", "Casablanca, Chile"),
    ]

    from services.port_manager import get_carrier_search_query
    for orig, res, expected in query_cases:
        query = get_carrier_search_query(orig, res)
        success = query == expected
        print(f"[{'PASS' if success else 'FAIL'}] Input: '{orig}' | Resolved: '{res}' | Query: '{query}' | Expected: '{expected}'")

if __name__ == "__main__":
    test()

