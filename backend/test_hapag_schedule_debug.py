# -*- coding: utf-8 -*-
"""
Debug script: Reuse HapagLloydConnector login, then step through the Schedule
page and take screenshots at each critical step.
"""
import os
import asyncio
from dotenv import load_dotenv
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

load_dotenv()

ORIGIN          = "SGSIN"
DEST            = "MYPKG"
CONTAINER_TYPE  = "DRY 40H"
CONTAINER_LABEL = "40' General Purpose High Cube"
SCRDIR          = "scratch"

os.makedirs(SCRDIR, exist_ok=True)


async def ss(page, name):
    path = f"{SCRDIR}/sched_{name}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [SS] {path}")


async def run():
    connector = HapagLloydConnector()
    request = RateSearchRequest(
        origin=ORIGIN,
        destination=DEST,
        container_type=CONTAINER_TYPE,
        container_quantity=1,
        weight_per_container_kg=20000,
        departure_date="tomorrow",
        carriers=["HAPAG_LLOYD"],
    )

    try:
        # ── 1. Login via connector (handles Azure B2C) ───────────────────────
        print("[1] Logging in via connector...")
        logged_in = await connector.login()
        if not logged_in:
            print("  [ERROR] Login failed — aborting.")
            return
        print("  Login OK.")
        page = connector.page

        # ── 2. Navigate to Schedule page ─────────────────────────────────────
        print("[2] Navigating to Schedule page...")
        await page.goto("https://www.hapag-lloyd.com/solutions/schedule/#/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            pass
        await asyncio.sleep(3)
        await ss(page, "02_schedule_landed")

        # Dismiss any modals
        for sel in ['button:has-text("Accept")', 'button:has-text("Agree")',
                    'button:has-text("Close")', '[aria-label="Close"]']:
            try:
                if await page.locator(sel).first.is_visible(timeout=800):
                    await page.locator(sel).first.click()
                    await asyncio.sleep(0.5)
            except:
                pass

        # ── 3. Inspect inputs ─────────────────────────────────────────────────
        print("[3] Inspecting inputs on Schedule page...")
        inputs = await page.locator('input').all()
        print(f"  Total inputs: {len(inputs)}")
        for i, inp in enumerate(inputs[:15]):
            try:
                phold = await inp.get_attribute("placeholder") or ""
                cls   = await inp.get_attribute("class") or ""
                vis   = await inp.is_visible()
                typ   = await inp.get_attribute("type") or ""
                print(f"  [{i}] type='{typ}' placeholder='{phold}' class='{cls[:50]}' visible={vis}")
            except:
                pass

        # ── 4. Fill Start Location (Origin) ──────────────────────────────────
        print("[4] Filling Start Location (Origin)...")
        # Try the specific selectors used by the actual connector method
        start_selectors = [
            'xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]',
            'input:below(:text("Start Location"))',
            'div:has-text("Start Location") input',
            'input[placeholder*="Location" i]',
            'input[type="text"]',
        ]
        start_field = None
        for sel in start_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=2000):
                    start_field = loc
                    print(f"  Start input found: {sel}")
                    break
            except:
                pass
        if not start_field:
            start_field = page.locator('input').first

        await start_field.scroll_into_view_if_needed()
        await start_field.click()
        await asyncio.sleep(0.4)
        await start_field.press("Control+A")
        await start_field.press("Backspace")
        await start_field.type(ORIGIN, delay=60)
        await asyncio.sleep(2)
        await ss(page, "04_origin_typed")

        # List dropdown options
        opts = await page.locator('.q-item, .hl-suggestion, [role="option"]').all()
        print(f"  Dropdown options after typing '{ORIGIN}': {len(opts)}")
        for o in opts[:5]:
            try:
                txt = (await o.inner_text()).strip().replace("\n", " ")
                print(f"    '{txt[:80]}'")
            except:
                pass

        # Click first option
        try:
            first_opt = page.locator('.q-item, .hl-suggestion, [role="option"]').first
            if await first_opt.is_visible(timeout=3000):
                await first_opt.click()
                print("  Origin selected.")
        except Exception as e:
            print(f"  Origin option click failed: {e}")
        await asyncio.sleep(1.5)
        await ss(page, "05_origin_selected")

        # ── 5. Fill End Location (Destination) ───────────────────────────────
        print("[5] Filling End Location (Destination)...")
        end_selectors = [
            'xpath=(//*[contains(text(), "End Location")])[1]/following::input[1]',
            'input:below(:text("End Location"))',
            'div:has-text("End Location") input',
            'input[type="text"]',
        ]
        end_field = None
        for sel in end_selectors:
            try:
                if sel == 'input[type="text"]':
                    loc = page.locator(sel).nth(1)
                else:
                    loc = page.locator(sel).first
                if await loc.is_visible(timeout=2000):
                    end_field = loc
                    print(f"  End input found: {sel}")
                    break
            except:
                pass
        if not end_field:
            end_field = page.locator('input').nth(1)

        await end_field.scroll_into_view_if_needed()
        await end_field.click()
        await asyncio.sleep(0.4)
        await end_field.press("Control+A")
        await end_field.press("Backspace")
        await end_field.type(DEST, delay=60)
        await asyncio.sleep(2)
        await ss(page, "06_dest_typed")

        opts2 = await page.locator('.q-item, .hl-suggestion, [role="option"]').all()
        print(f"  Dropdown options after typing '{DEST}': {len(opts2)}")
        for o in opts2[:5]:
            try:
                txt = (await o.inner_text()).strip().replace("\n", " ")
                print(f"    '{txt[:80]}'")
            except:
                pass

        try:
            first_opt2 = page.locator('.q-item, .hl-suggestion, [role="option"]').first
            if await first_opt2.is_visible(timeout=3000):
                await first_opt2.click()
                print("  Destination selected.")
        except Exception as e:
            print(f"  Dest option click failed: {e}")
        await asyncio.sleep(1.5)
        await ss(page, "07_dest_selected")

        # ── 6. Advanced Search Toggle ─────────────────────────────────────────
        print("[6] Inspecting page for 'Advanced search' toggle...")

        # JS scan for all matching elements
        adv_elements = await page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            return all
                .filter(el => {
                    const t = (el.textContent || '').trim().toLowerCase();
                    // Only leaf-like nodes — children shouldn't also match
                    const childMatch = Array.from(el.children).some(c =>
                        (c.textContent || '').trim().toLowerCase().includes('advanced')
                    );
                    return (t.includes('advanced') && !childMatch);
                })
                .slice(0, 10)
                .map(el => ({
                    tag: el.tagName,
                    cls: (el.className || '').substring(0, 80),
                    txt: (el.textContent || '').trim().substring(0, 80),
                    visible: el.offsetParent !== null,
                    href: el.href || null
                }));
        }""")
        print(f"  Elements containing 'advanced': {len(adv_elements)}")
        for el in adv_elements:
            print(f"    tag={el['tag']} visible={el['visible']} txt='{el['txt']}' cls='{el['cls'][:50]}'")

        # Try clicking Advanced search with multiple selectors
        adv_selectors = [
            ':text("Advanced search")',
            ':text-is("Advanced search")',
            'text=Advanced search',
            'button:has-text("Advanced")',
            'a:has-text("Advanced")',
            'span:has-text("Advanced search")',
            '[class*="advanced"]',
        ]
        adv_clicked = False
        for sel in adv_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=1000):
                    tag = await loc.evaluate("el => el.tagName")
                    txt = (await loc.inner_text()).strip()
                    print(f"  Found Advanced search: sel='{sel}' tag={tag} txt='{txt}'")
                    await loc.click()
                    adv_clicked = True
                    print("  Clicked Advanced search!")
                    await asyncio.sleep(1.5)
                    break
            except:
                pass

        if not adv_clicked:
            print("  [WARN] Could not click Advanced search with any selector")

        await ss(page, "08_after_advanced_toggle")

        # ── 7. Inspect inputs after Advanced Search expansion ─────────────────
        print("[7] Inspecting inputs after Advanced search expanded...")
        inputs2 = await page.locator('input').all()
        print(f"  Total inputs now: {len(inputs2)}")
        for i, inp in enumerate(inputs2[:20]):
            try:
                phold = await inp.get_attribute("placeholder") or ""
                cls   = await inp.get_attribute("class") or ""
                vis   = await inp.is_visible()
                typ   = await inp.get_attribute("type") or ""
                aria  = await inp.get_attribute("aria-label") or ""
                print(f"  [{i}] type='{typ}' aria='{aria}' placeholder='{phold}' class='{cls[:50]}' visible={vis}")
            except:
                pass

        # JS: Find elements containing "Container Type"
        ct_elements = await page.evaluate("""() => {
            const all = Array.from(document.querySelectorAll('*'));
            return all
                .filter(el => {
                    const t = (el.textContent || '').trim().toLowerCase();
                    const childMatch = Array.from(el.children).some(c =>
                        (c.textContent || '').trim().toLowerCase().includes('container type')
                    );
                    return t.includes('container type') && !childMatch;
                })
                .slice(0, 8)
                .map(el => ({
                    tag: el.tagName,
                    cls: (el.className || '').substring(0, 80),
                    txt: (el.textContent || '').trim().substring(0, 80),
                    visible: el.offsetParent !== null
                }));
        }""")
        print(f"  'Container Type' elements: {len(ct_elements)}")
        for el in ct_elements:
            print(f"    tag={el['tag']} visible={el['visible']} txt='{el['txt']}' cls='{el['cls'][:50]}'")

        # Count q-select__focus-target inputs
        q_selects = page.locator('input.q-select__focus-target')
        q_count = await q_selects.count()
        print(f"  q-select__focus-target count: {q_count}")
        for i in range(q_count):
            vis = await q_selects.nth(i).is_visible()
            print(f"    [{i}] visible={vis}")

        # ── 8. Click Container Type dropdown ──────────────────────────────────
        print("[8] Clicking container type dropdown...")
        # The container type is typically the LAST q-select on the page
        # (after Start Location and End Location selects)
        ct_box = None
        ct_selectors = [
            'xpath=(//*[contains(text(), "Container Type")])[last()]/following::input[1]',
            'xpath=(//*[contains(text(), "Container Type")])[1]/following::input[1]',
        ]
        for sel in ct_selectors:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=2000):
                    ct_box = loc
                    print(f"  Container type input via: {sel}")
                    break
            except Exception as e:
                print(f"  {sel} -> {e}")

        if not ct_box and q_count > 0:
            # Use the last q-select (container type appears after origin/dest)
            for idx in range(q_count - 1, -1, -1):
                if await q_selects.nth(idx).is_visible():
                    ct_box = q_selects.nth(idx)
                    print(f"  Using q-select__focus-target at index {idx}")
                    break

        if ct_box:
            await ct_box.scroll_into_view_if_needed()
            await ct_box.click(timeout=5000)
            print("  Container type dropdown clicked.")
            await asyncio.sleep(1.5)
            await ss(page, "09_container_dropdown_open")

            # List options
            all_opts = await page.locator('.q-item, .q-menu .q-item, [role="option"]').all()
            print(f"  Dropdown options: {len(all_opts)}")
            for o in all_opts[:15]:
                try:
                    txt = (await o.inner_text()).strip().replace("\n", " ")
                    print(f"    '{txt[:80]}'")
                except:
                    pass

            # Select the right one
            target = page.locator(f'.q-item:has-text("{CONTAINER_LABEL}"), [role="option"]:has-text("{CONTAINER_LABEL}")').first
            if await target.is_visible(timeout=3000):
                await target.click()
                print(f"  Selected '{CONTAINER_LABEL}'")
            else:
                # Try partial match with "High Cube"
                target2 = page.locator('.q-item:has-text("High Cube"), [role="option"]:has-text("High Cube")').first
                if await target2.is_visible(timeout=2000):
                    txt2 = (await target2.inner_text()).strip()
                    await target2.click()
                    print(f"  Selected partial match: '{txt2}'")
                else:
                    print(f"  [WARN] Could not find container option '{CONTAINER_LABEL}'")
        else:
            print("  [WARN] Container type dropdown input NOT found!")

        await asyncio.sleep(1)
        await ss(page, "10_container_selected")

        # ── 9. Click Search ───────────────────────────────────────────────────
        print("[9] Clicking Search button...")
        search_btn = None
        search_selectors = [
            'button:has-text("Search")',
            'button[type="submit"]',
            'span:has-text("Search")',
        ]
        for sel in search_selectors:
            try:
                locs = page.locator(sel)
                count = await locs.count()
                print(f"  '{sel}': {count} elements")
                for idx in range(count):
                    if await locs.nth(idx).is_visible():
                        search_btn = locs.nth(idx)
                        print(f"  Using search button at index {idx} via '{sel}'")
                        break
                if search_btn:
                    break
            except:
                pass

        if search_btn:
            await search_btn.scroll_into_view_if_needed()
            await search_btn.click()
            print("  Search clicked.")
        else:
            print("  [WARN] Search button not found!")

        await asyncio.sleep(6)
        await ss(page, "11_after_search")

        # Wait for results
        print("[10] Waiting for results (up to 45s)...")
        try:
            await page.wait_for_selector(
                'button:has-text("Show Details"), div:has-text("Available sailings"), div:has-text("Voyage no")',
                timeout=45000
            )
            print("  Results loaded!")
        except Exception as e:
            print(f"  Timeout: {e}")
        await ss(page, "12_results")

        # Scrape what we got
        schedules = await page.evaluate(r'''() => {
            const results = [];
            const voyageEls = Array.from(document.querySelectorAll('*')).filter(el => {
                const t = (el.textContent || '');
                if (!t.includes('Voyage no')) return false;
                return !Array.from(el.children).some(c => (c.textContent || '').includes('Voyage no'));
            });
            voyageEls.forEach(el => {
                let card = el.parentElement;
                for (let d = 0; d < 10; d++) {
                    if (!card) break;
                    const t = (card.textContent || '');
                    if (t.includes('Voyage no') && (t.includes('Show Details') || t.includes('Quote Now'))) break;
                    card = card.parentElement;
                }
                if (!card) return;
                const text = (card.textContent || '').replace(/\s+/g, ' ');
                const dates = text.match(/\d{4}-\d{2}-\d{2}/g) || [];
                if (dates.length < 2) return;
                const vmatch = text.match(/Voyage no\s*\.?\s*:\s*(\S+)/i);
                results.push({
                    etd: dates[0],
                    eta: dates[1],
                    voyage: vmatch ? vmatch[1] : '',
                    text_snippet: text.substring(0, 120)
                });
            });
            return results;
        }''')
        print(f"\n  Scraped {len(schedules)} sailings:")
        for s in schedules:
            print(f"    ETD={s['etd']} ETA={s['eta']} Voyage={s['voyage']}")

    finally:
        await connector.close()
        print("\nDone. Check scratch/sched_*.png for screenshots.")


if __name__ == "__main__":
    asyncio.run(run())
