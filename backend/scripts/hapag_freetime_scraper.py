import asyncio
import os
import sys
import re
import json
import traceback

# Ensure we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carriers.hapag_lloyd_connector import HapagLloydConnector
import pdfplumber

async def scrape_hapag_freetime():
    print("Starting Hapag-Lloyd Freetime Scraper...")
    
    # Initialize the connector
    connector = HapagLloydConnector()
    try:
        login_success = await connector.login()
        
        if not login_success:
            print("Failed to log in to Hapag-Lloyd. Cannot proceed.")
            return

        page = connector.page
        
        regions = [
            "latin-america",
            "europe",
            "asia",
            "middle-east",
            "africa",
            "north-america"
        ]
        
        base_url = "https://www.hapag-lloyd.com/en/online-business/quotation/detention-demurrage/{region}.html"
        
        scratch_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch", "hapag_pdfs")
        os.makedirs(scratch_dir, exist_ok=True)
        
        freetime_dict = {}
        
        for region in regions:
            url = base_url.format(region=region)
            print(f"\nNavigating to {url}")
            await page.goto(url)
            await page.wait_for_timeout(3000)
            
            # Find all links containing '.pdf'
            links = await page.locator('a[href*=".pdf"]').all()
            
            print(f"Found {len(links)} PDF links on {region}")
            
            for link in links:
                try:
                    text = await link.inner_text()
                    href = await link.get_attribute('href')
                    if not href or ".pdf" not in href.lower():
                        continue
                        
                    text_lower = text.lower()
                    href_lower = href.lower()
                        
                    # Skip if it is strictly an EXPORT document (contains export but not import)
                    if "export" in text_lower and "import" not in text_lower:
                        continue
                    if "export" in href_lower and "import" not in href_lower:
                        continue
                        
                    # We are looking for anything related to detention, demurrage, or tariffs
                    is_valid = any(word in text_lower for word in ["detention", "demurrage", "dnd", "dtd", "dmd", "mhd", "mho", "tariff"]) or \
                               any(word in href_lower for word in ["detention", "demurrage", "dnd", "dtd", "dmd", "mhd", "mho", "tariff"])
                    
                    if is_valid:
                        # Clean up country name extraction robustly
                        # E.g. "Albania Demurrage Detention Import"
                        # E.g. "06012025_Barbados_Import_Detention_Demurrage.pdf"
                        
                        country = text.split("Detention")[0].split("Demurrage")[0].split("Import")[0].strip()
                        
                        if not country or len(country) < 3:
                            file_name = href.split("/")[-1]
                            country = file_name.split("_Detention")[0].split("_Demurrage")[0].split("_Import")[0].split("-Detention")[0].split("-Demurrage")[0].split("-Import")[0].split("_MHD")[0].split("_DMD")[0].strip()
                            country = re.sub(r"^\d+_", "", country)
                            country = country.replace("_", " ")
                            
                        # Edge case fallback for weird parsing
                        if country.lower() == "cambodia import detention":
                            country = "Cambodia"
                            
                        if not country:
                            print(f"Could not parse country from: {text} / {href}")
                            continue
                            
                        if not href.startswith("http"):
                            href = "https://www.hapag-lloyd.com" + href
                            
                        pdf_path = os.path.join(scratch_dir, f"{country.replace(' ', '_')}.pdf")
                        
                        print(f"Downloading PDF for {country} from {href}...")
                        
                        # Actually, let's use page.request.get to download it directly using the authenticated session!
                        response = await page.request.get(href)
                        if response.status == 200:
                            body = await response.body()
                            with open(pdf_path, "wb") as f:
                                f.write(body)
                            print(f"Saved {pdf_path}")
                            
                            # Now parse it
                            freetimes = parse_hapag_pdf(pdf_path)
                            if freetimes:
                                print(f"-> Found Freetime for {country}: {freetimes}")
                                freetime_dict[country] = freetimes
                            else:
                                print(f"-> Could not find Freetime in PDF for {country}")
                        else:
                            print(f"Failed to download {href}: Status {response.status}")
                except Exception as e:
                    print(f"Error processing link: {e}")
                    
        # Save config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "hapag_freetime.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(freetime_dict, f, indent=4)
            
        print(f"\nScraping complete! Config saved to {config_path}")
        
    except Exception as e:
        print(f"Scraper error: {e}")
        traceback.print_exc()
    finally:
        await connector.close()

def parse_hapag_pdf(pdf_path: str):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            
            # Using extract_text and regex might be more robust than extract_table 
            # because tables can span pages or have weird merged headers.
            text = first_page.extract_text()
            lines = text.split("\n")
            
            for line in lines:
                # We are looking for a line containing "Freetime" and then numbers
                # "Cambodia All ports Detention Freetime 7 7"
                # "Australia All ports Demurrage Freetime 8 Free 8 Free 8 Free 8 Free"
                if "Freetime" in line:
                    # Look for standalone digits.
                    # Usually, the first digit is 20GP, the second digit is 40GP/40HC.
                    # Or it might be "7 -- Free 7 -- Free"
                    numbers = re.findall(r"\b\d{1,2}\b", line)
                    if len(numbers) >= 2:
                        return {
                            "20GP": int(numbers[0]),
                            "40GP": int(numbers[1])
                        }
                    
            return None
    except Exception as e:
        print(f"PDF Parsing error for {pdf_path}: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(scrape_hapag_freetime())
