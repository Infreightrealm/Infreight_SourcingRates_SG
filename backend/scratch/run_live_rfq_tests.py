"""
Scratch script to execute all 4 user email examples through LIVE Gemini API (gemini-2.5-flash).
"""
import asyncio
import json
import os
import sys

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(".env")

# Ensure RFQ_AGENT_MOCK is FALSE for live test
os.environ["RFQ_AGENT_MOCK"] = "false"
if "PYTEST_CURRENT_TEST" in os.environ:
    del os.environ["PYTEST_CURRENT_TEST"]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.rfq_agent import parse_rfq

EMAIL_1 = """Dear All,
Please quote cheap and best EXW airfreight rates;
Collect from:
Hitachi Asia Ltd
Industrial Components and Equipment Group (ICE)
30 Pioneer Crescent #10-15, West Park Bizcentral, Singapore 628560

Commodity: HITACHI PRINTERS -LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970
Dim: 64x53x74 cm/10 pkgs
Gross weight: 320 kg
HS CODE: 84433100

Best Regards,
Mohammed Shamnad
Manager - Airfreight
Airlift Logistics"""

EMAIL_2 = """Hi Glenn,

Good Day
Kindly advise us air rates for below:
POL: Singapore Airport
POD: KUL
Commodity: Machines Part Accessories - Docking Roller Assy / Trial Cutter Roller Assy Bottom Surface
2 Crates / Sets
Dimension of each crate:
186 x 32 x 37 cm H - 2 Crates
Gross Weight: 320.00 kgs
(160 kgs x 2 crates)
Please also provide available flight schedule and transit time.
Thank you"""

EMAIL_3 = """Hi Jing Hui,

Good Day
Kindly advise us air rates for below:
POL: Singapore Airport
POD: KUL
Commodity: Machines Part Accessories - Docking Roller Assy / Trial Cutter Roller Assy Bottom Surface
2 Crates / Sets
Dimension of each crate:
186 x 32 x 37 cm H - 2 Crates
Gross Weight: 320.00 kgs
(160 kgs x 2 crates)
Please also provide available flight schedule and transit time.
Thank you."""

EMAIL_4 = """Hi Toby, Shona and Bethy.

Good day.

Please compile rates from ex Pasir Gudang / Tanjung Pelepas for 20' & 40' as follows.

Commodity: Steel Plate, Steel Coil.

1) Koper, Slovenia
2) Nagoya, Japan
4) Thessaloniki, Greece
5) Liverpool, England
6) Colombo, Sri Lanka
7) Chiba, Japan
8) Montreal, Canada
9) Baltimore, US
10) Toronto (Halifax), Canada
11) Toronto (Vancouver), Canada
12) Winnipeg, Canada
13) Vancouver, Canada
14) Houston, US
15) Kaohsiung, Taiwan
16) Chattogram, Bangladesh
17) Manzanillo, Mexico
18) Bourges, France"""


async def run():
    print("================ LIVE GEMINI EXTRACTION RESULTS ================")
    
    print("\n--- EMAIL 1 (Hitachi Lithium Batteries Airfreight) ---")
    r1 = await parse_rfq(EMAIL_1)
    print(f"Mode: {r1.mode} | Confidence: {r1.confidence} | DG: {r1.is_dangerous_goods}")
    print(f"Matched Keywords: {r1.matched_keywords}")
    print(f"Compliance Notes: {r1.compliance_notes}")
    print(f"HS Code: {r1.hs_code}")
    print(f"Air Drafts Count: {len(r1.air_drafts or [])}")
    if r1.air_drafts:
        print("Draft 1 (AWOT):", r1.air_drafts[0]["email_subject"])
        print("Draft 2 (ASPAC):", r1.air_drafts[1]["email_subject"])

    print("\n--- EMAIL 2 (Air Rates to Glenn) ---")
    r2 = await parse_rfq(EMAIL_2)
    print(f"Mode: {r2.mode} | Confidence: {r2.confidence}")
    print(f"Matched Keywords: {r2.matched_keywords}")
    print(f"Air Drafts Count: {len(r2.air_drafts or [])}")

    print("\n--- EMAIL 3 (Air Rates to Jing Hui) ---")
    r3 = await parse_rfq(EMAIL_3)
    print(f"Mode: {r3.mode} | Confidence: {r3.confidence}")
    print(f"Matched Keywords: {r3.matched_keywords}")
    print(f"Air Drafts Count: {len(r3.air_drafts or [])}")

    print("\n--- EMAIL 4 (Steel Plate Multi-Origin Multi-Destination Ocean) ---")
    r4 = await parse_rfq(EMAIL_4)
    print(f"Mode: {r4.mode} | Confidence: {r4.confidence}")
    print(f"Matched Keywords: {r4.matched_keywords}")
    print(f"Total Expanded Pairs Found: {r4.total_pairs_found}")
    print(f"Pairs Omitted Count: {r4.pairs_omitted_count}")
    print(f"Parsed Pairs (First 5):")
    if r4.all_parsed_pairs:
        for p in r4.all_parsed_pairs[:5]:
            print("  -", p["origin"], "-->", p["destination"])

if __name__ == "__main__":
    asyncio.run(run())
