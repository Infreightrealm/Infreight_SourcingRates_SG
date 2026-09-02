import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ["RFQ_AGENT_MOCK"] = "true"

sys.path.insert(0, os.path.abspath("backend"))
from services.rfq_agent import parse_rfq


async def test_live():
    print("=== TESTING LIVE GEMINI 2.5 FLASH WITH OCEAN FCL STRESS TEST ENQUIRY ===")
    rfq_text = (
        "Please quote 1 x 40RF Singapore to Sydney, frozen seafood,\n"
        "temperature -18C, 22 MT, ETD early September.\n\n"
        "Best Regards,\n\n"
        "Michael Tan\n"
        "Director – Logistics\n"
        "Global Trade Pte Ltd\n"
        "50 Raffles Place #22-01, Singapore 048623\n"
        "Mob: +65 9123 4567 | Tel: +65 6222 8888\n"
        "michael@globaltrade.com.sg | www.globaltrade.com.sg"
    )


    
    res = await parse_rfq(rfq_text)
    print(f"Mode: {res.mode}")
    print(f"Status: {res.status}")
    if res.status == "needs_clarification":
        print(f"Clarification Question: {res.clarification_question}")
        print(f"Missing Fields: {res.missing_fields}")
    elif res.parsed_fields:
        print(f"Origin: {res.parsed_fields.origin}")
        print(f"Destination: {res.parsed_fields.destination}")
        print(f"Container Type: {res.parsed_fields.container_type}")
        print(f"Container Quantity: {res.parsed_fields.container_quantity}")
        print(f"Weight per container (KG): {res.parsed_fields.weight_per_container_kg}")
        print(f"Commodity: {res.parsed_fields.commodity}")

if __name__ == "__main__":
    asyncio.run(test_live())
