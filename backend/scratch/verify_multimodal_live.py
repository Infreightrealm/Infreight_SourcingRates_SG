import asyncio
import base64
import os
import sys
from PIL import Image, ImageDraw
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath("backend"))
from services.rfq_agent import parse_rfq


def create_email_screenshot(text: str, filename: str) -> tuple[str, str]:
    img = Image.new("RGB", (700, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    # Draw header box to simulate email client
    d.rectangle([0, 0, 700, 40], fill=(240, 242, 245))
    d.text((15, 12), "Inbox - Enquiry Email Message", fill=(50, 50, 50))
    d.text((20, 60), text, fill=(20, 20, 20))
    
    img_path = os.path.abspath(filename)
    img.save(img_path)
    
    with open(img_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    return b64_data, "image/png"

async def verify_live_images():
    print("=== VERIFYING LIVE GEMINI 2.5 FLASH MULTIMODAL VISION PATH ===\n")

    # Test 1: Hi Glenn Air Email Screenshot
    air_text = (
        "Hi Glenn,\n\n"
        "Good Day\n"
        "Kindly advise us air rates for below:\n"
        "POL: Singapore Airport\n"
        "POD: KUL\n"
        "Commodity: Machines Part Accessories\n"
        "2 Crates / Sets\n"
        "Dimension: 186 x 32 x 37 cm H - 2 Crates\n"
        "Gross Weight: 320.00 kgs (160 kgs x 2 crates)\n"
        "Please also provide available flight schedule and transit time. Thank you"
    )
    b64_air, mime_air = create_email_screenshot(air_text, "air_glenn_screenshot.png")
    
    print("[1] Parsing Air Freight Email Screenshot (Hi Glenn)...")
    res_air = await parse_rfq(raw_text="", image_b64=b64_air, image_mime=mime_air)
    print(f"Status: {res_air.status}")
    print(f"Mode: {res_air.mode}")
    print(f"POL Airport Display: {res_air.origin_display}")
    print(f"POD Airport Display: {res_air.destination_display}")
    print(f"Drafts generated: {len(res_air.air_drafts or [])}")
    for idx, d in enumerate(res_air.air_drafts or []):
        print(f"  Draft #{idx+1} to {d['company_name']} ({d['contact_person']}): {d['contact_email']}")
    print("\n" + "-"*60 + "\n")

    # Test 2: Pak Shaun Ocean Email Screenshot
    sea_text = (
        "Hi team, need rate for 10x20GP from PK to JKT. Urgent for this week.\n"
        "Also have another 15x20 and 10x20 coming up next week.\n"
        "Using 2 forwarders currently, please try USD 70-80 target rate if possible. Thanks, Pak Shaun."
    )
    b64_sea, mime_sea = create_email_screenshot(sea_text, "pak_shaun_screenshot.png")

    print("[2] Parsing Ocean Freight Email Screenshot (Pak Shaun)...")
    res_sea = await parse_rfq(raw_text="", image_b64=b64_sea, image_mime=mime_sea)
    print(f"Status: {res_sea.status}")
    print(f"Mode: {res_sea.mode}")
    print(f"POL Port Display: {res_sea.origin_display}")
    print(f"POD Port Display: {res_sea.destination_display}")
    if res_sea.parsed_fields:
        print(f"Pre-filled Route: {res_sea.parsed_fields.origin} -> {res_sea.parsed_fields.destination}")
        print(f"Container Types: {res_sea.parsed_fields.container_types}")
    if res_sea.sales_notes:
        print(f"Sales Desk Notes: {res_sea.sales_notes}")

if __name__ == "__main__":
    asyncio.run(verify_live_images())
