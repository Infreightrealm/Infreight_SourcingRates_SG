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

    print("\nTesting resolve_port_for_carrier...")
    test_cases = [
        ("VN HPH", "maersk", "Haiphong"),
        ("VN HPH", "one", "Hai Phong"),
        ("Haiphong (VN HPH)", "maersk", "Haiphong"),
        ("Haiphong (VN HPH)", "one", "Hai Phong"),
        ("Haiphong", "maersk", "Haiphong"),
        ("Haiphong", "one", "Hai Phong"),
        ("Hai Phong", "maersk", "Haiphong"),
        ("Hai Phong", "one", "Hai Phong"),
        ("Ho Chi Minh City", "maersk", "Ho Chi Minh City"),
        ("Ho Chi Minh City", "one", "Ho Chi Minh"),
        ("VNSGN", "maersk", "Ho Chi Minh City"),
        ("VNSGN", "one", "Ho Chi Minh"),
        ("Singapore (SGSIN)", "maersk", "Singapore"),
        ("Singapore (SGSIN)", "one", "Singapore"),
    ]

    for q, carrier, expected in test_cases:
        resolved = resolve_port_for_carrier(q, carrier)
        success = resolved == expected
        print(f"[{'PASS' if success else 'FAIL'}] Input: '{q}' -> Carrier: {carrier} | Resolved: '{resolved}' | Expected: '{expected}'")

if __name__ == "__main__":
    test()

