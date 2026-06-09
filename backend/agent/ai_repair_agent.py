"""
AI Repair Agent — diagnoses Playwright step failures and suggests selector repairs using Gemini.
"""
import os
import re
import json
import httpx
from bs4 import BeautifulSoup

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

async def suggest_fix(context: dict, dom_file_path: str = None) -> dict:
    """
    Analyzes the failure context and DOM content to suggest a selector repair.
    Uses Gemini API if GEMINI_API_KEY is present; otherwise falls back to local rule-based recovery.
    """
    # Load DOM content
    dom_content = ""
    if dom_file_path and os.path.exists(dom_file_path):
        try:
            with open(dom_file_path, "r", encoding="utf-8") as f:
                # Truncate DOM if too large to fit comfortably in LLM context
                dom_content = f.read(120000)
        except Exception as e:
            print(f"[AI Repair] Error reading DOM file: {e}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[AI Repair] GEMINI_API_KEY not configured. Falling back to local rule-based selector analyzer.")
        return _local_fuzzy_repair(context, dom_content)

    # Clean/sanitize DOM content to save prompt token window
    soup = BeautifulSoup(dom_content, "html.parser")
    # Remove script and style tags to make it readable
    for tag in soup(["script", "style", "svg", "path", "head", "meta"]):
        tag.decompose()
    sanitized_dom = soup.prettify()[:50000] # Limit to 50k chars

    prompt = f"""You are an expert Playwright automation self-healing agent.
We had a selector failure during browser automation for carrier rates.

Context:
- Carrier: {context.get('carrier')}
- Failed Step: {context.get('step_name')}
- Expected Action: {context.get('expected_action')}
- Current URL: {context.get('url')}
- Failed Selector: {context.get('original_selector')}
- Playwright Error: {context.get('error_message')}

Below is the sanitized DOM HTML of the page:
```html
{sanitized_dom}
```

Please analyze the DOM and locate the correct replacement element for the expected action.
Return a JSON object containing:
1. "suggested_selector": The new Playwright selector (e.g. 'button:has-text("View Quote")', 'input[name="departureDate"]', 'div[class*="search"]')
2. "reasoning": A clear explanation of why the selector changed and why this new locator is correct.
3. "risk_level": "LOW", "MEDIUM", or "HIGH" based on the likelihood of matching the wrong element or breaking future runs.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "suggested_selector": {"type": "STRING"},
                    "reasoning": {"type": "STRING"},
                    "risk_level": {"type": "STRING", "enum": ["LOW", "MEDIUM", "HIGH"]}
                },
                "required": ["suggested_selector", "reasoning", "risk_level"]
            }
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={api_key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=20.0
            )
            
            if response.status_code == 200:
                data = response.json()
                text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(text_response)
                print(f"[AI Repair] Gemini generated selector suggestion: '{result.get('suggested_selector')}' (Risk: {result.get('risk_level')})")
                return result
            else:
                print(f"[AI Repair] Gemini API error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[AI Repair] Gemini API request failed: {e}")

    # Fallback to local repair if Gemini fails
    return _local_fuzzy_repair(context, dom_content)


def _local_fuzzy_repair(context: dict, dom_content: str) -> dict:
    """
    A local rule-based heuristic to locate reasonable buttons or inputs
    when Gemini API is unavailable.
    """
    step_name = context.get("step_name", "").lower()
    original_selector = context.get("original_selector", "")
    expected_action = context.get("expected_action", "").lower()
    
    # Heuristics: search for text labels based on step intent
    intent_words = []
    if "button" in original_selector or "click" in step_name or "click" in expected_action:
        # Action is likely clicking a button/link
        if "quote" in step_name or "quote" in expected_action:
            intent_words = ["quote", "rate", "search", "getquote", "viewquote", "submit", "find"]
        elif "login" in step_name or "login" in expected_action:
            intent_words = ["login", "signin", "submit", "enter"]
        elif "calendar" in step_name or "date" in step_name:
            intent_words = ["calendar", "date", "picker"]
            
        # Parse DOM to find button candidates
        if dom_content:
            soup = BeautifulSoup(dom_content, "html.parser")
            candidates = []
            
            # Find buttons and links
            for element in soup.find_all(["button", "a", "input"]):
                original_text = (element.text or element.get("value") or element.get("placeholder") or "").strip()
                text_lower = original_text.lower()
                role = element.get("role", "").lower()
                type_attr = element.get("type", "").lower()
                
                # Filter buttons
                if element.name == "button" or role == "button" or type_attr == "submit" or element.name == "a":
                    candidates.append((element, original_text, text_lower))
                    
            # Try to match intent words
            for cand, original_text, text_lower in candidates:
                for word in intent_words:
                    if word in text_lower and len(original_text) < 30: # reasonable button label length
                        # Build a clean playwright selector
                        clean_text = original_text.replace('"', '\\"').strip()
                        suggestion = f'button:has-text("{clean_text}")' if cand.name == "button" else f'a:has-text("{clean_text}")'
                        
                        return {
                            "suggested_selector": suggestion,
                            "reasoning": f"Local parser found a clickable element '<{cand.name}>' containing the text label '{clean_text}' which matches intent '{word}' in step '{step_name}'.",
                            "risk_level": "MEDIUM"
                        }
                        
    # Ultimate fallback if no match
    return {
        "suggested_selector": original_selector, # cannot repair
        "reasoning": "Could not suggest a replacement selector. No matching text heuristics were found.",
        "risk_level": "HIGH"
    }
