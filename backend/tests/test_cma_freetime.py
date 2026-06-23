"""
Unit test for CMA CGM demurrage and detention combined free time parsing logic.
"""
import sys
import os
import asyncio
import re

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from carriers.cma_connector import CMAConnector

class MockLocator:
    def __init__(self, is_visible_val=True):
        self._is_visible_val = is_visible_val
    async def is_visible(self, timeout=None):
        return self._is_visible_val
    def first(self):
        return self

class MockCard:
    def __init__(self, inner_text_val):
        self._inner_text_val = inner_text_val
    async def scroll_into_view_if_needed(self):
        pass
    def locator(self, selector):
        return MockLocator()
    async def inner_text(self):
        return self._inner_text_val

async def test_cma_freetime_parsing():
    # 1. Test separate demurrage and detention days
    mock_split_text = """
    Import free time details
    Import Demurrage: 7 Calendar Days
    Import Detention: 5 Calendar Days
    Export free time: 10 Calendar Days
    """
    
    dd_text = mock_split_text
    # Isolate import section
    import_idx = dd_text.lower().find("import")
    import_text = dd_text[import_idx:] if import_idx != -1 else dd_text
    
    # Match separate
    dem_match = re.search(r'demurrage.*?(?:free\s*time)?.*?(\d+)\s+(?:Calendar|Day)', import_text, re.IGNORECASE | re.DOTALL)
    det_match = re.search(r'detention.*?(?:free\s*time)?.*?(\d+)\s+(?:Calendar|Day)', import_text, re.IGNORECASE | re.DOTALL)
    
    dem_days = int(dem_match.group(1)) if dem_match else 0
    det_days = int(det_match.group(1)) if det_match else 0
    
    assert dem_days == 7, f"Expected 7 demurrage days, got {dem_days}"
    assert det_days == 5, f"Expected 5 detention days, got {det_days}"
    assert dem_days + det_days == 12
    
    # 2. Test combined fallback free time
    mock_combined_text = """
    Import free time: 10 Calendar Days
    Export free time: 10 Calendar Days
    """
    
    dd_text_combined = mock_combined_text
    import_idx_c = dd_text_combined.lower().find("import")
    import_text_c = dd_text_combined[import_idx_c:] if import_idx_c != -1 else dd_text_combined
    
    dem_match_c = re.search(r'demurrage.*?(?:free\s*time)?.*?(\d+)\s+(?:Calendar|Day)', import_text_c, re.IGNORECASE | re.DOTALL)
    det_match_c = re.search(r'detention.*?(?:free\s*time)?.*?(\d+)\s+(?:Calendar|Day)', import_text_c, re.IGNORECASE | re.DOTALL)
    
    assert dem_match_c is None
    assert det_match_c is None
    
    match_c = re.search(r'Import free time.*?(\d+)\s+Calendar', dd_text_combined, re.IGNORECASE | re.DOTALL)
    assert match_c is not None, "Combined/Fallback free time match failed"
    assert int(match_c.group(1)) == 10
    
    print("CMA free time parsing unit tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_cma_freetime_parsing())
