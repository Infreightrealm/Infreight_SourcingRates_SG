import re

def parse_msc_free_time(popup_inner: str) -> int:
    free_time = 0
    # Tier 1: Look for Import Combined section followed by Free Days / digit
    match = re.search(r"Import\s+Combined.*?(?:Free\s*Days\s*:?\s*|:\s*|\s+)(\d+)", popup_inner, re.IGNORECASE | re.DOTALL)
    if not match:
        # Tier 2: Look for Import section followed by Free Days / digit
        match = re.search(r"Import.*?(?:Free\s*Days\s*:?\s*|:\s*|\s+)(\d+)", popup_inner, re.IGNORECASE | re.DOTALL)
    if not match:
        # Tier 3: General Free Days match
        match = re.search(r"(?:Free\s*Days\s*:?\s*)(\d+)", popup_inner, re.IGNORECASE | re.DOTALL)

    if match:
        free_time = int(match.group(1))
    return free_time

# Test cases
sample_user_screenshot = """
Equipment type: 20DV   Est. Transit Time: 47 Days
Selected Charges  Quote Conditions  Schedule  Free Time

Export Combined
Free Days : 9 Calendar days

Import Combined
Free Days : 8 Working days without public holidays

*Free Time does not include Storage & Plug-in.
"""

sample_calendar = """
Export Combined
Free Days : 7 Calendar days

Import Combined
Free Days : 14 Calendar days
"""

sample_simple = """
Import Combined
8 Days
"""

print("User Screenshot Test:", parse_msc_free_time(sample_user_screenshot))
print("Calendar Test:", parse_msc_free_time(sample_calendar))
print("Simple Test:", parse_msc_free_time(sample_simple))

assert parse_msc_free_time(sample_user_screenshot) == 8
assert parse_msc_free_time(sample_calendar) == 14
assert parse_msc_free_time(sample_simple) == 8
print("ALL TESTS PASSED SUCCESSFULLY!")
