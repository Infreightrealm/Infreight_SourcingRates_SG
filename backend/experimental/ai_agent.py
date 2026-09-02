"""
AI Browser Agent — Vision-based browser automation using Gemini Flash.

This module provides a generic AI agent that can navigate websites by:
1. Taking screenshots of the current browser page
2. Sending them to Gemini's vision API with task instructions
3. Receiving structured actions (click, type, scroll, etc.)
4. Executing those actions via Playwright

This is EXPERIMENTAL and completely separate from the production carrier connectors.
"""
import os
import re
import json
import base64
import asyncio
import time
import traceback
from datetime import datetime
from typing import Optional

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# ────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — instructs Gemini on how to act as a browser agent
# ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an AI browser automation agent. You control a web browser by looking at screenshots and deciding what action to take next.

## Your Capabilities
You can perform these actions:
- **click(x, y)** — Click at pixel coordinates (x, y) on the page
- **type(text)** — Type text into the currently focused input field
- **clear_and_type(text)** — Select all text in the focused field, delete it, and type new text
- **press(key)** — Press a keyboard key (Enter, Tab, Escape, ArrowDown, ArrowUp, Backspace)
- **scroll(direction)** — Scroll the page ("up" or "down")
- **wait(seconds)** — Wait for the page to load (1-5 seconds)
- **done(result)** — Task is complete, return the result summary
- **fail(reason)** — Task cannot be completed, explain why

## Response Format
You MUST respond with ONLY a JSON object. No markdown, no explanation, no code fences.

Examples:
{"action": "click", "x": 450, "y": 320, "reason": "Clicking the 'From' input field"}
{"action": "type", "text": "Singapore", "reason": "Typing the origin port name"}
{"action": "press", "key": "Enter", "reason": "Submitting the search form"}
{"action": "scroll", "direction": "down", "reason": "Scrolling to see more results"}
{"action": "wait", "seconds": 3, "reason": "Waiting for dropdown to appear"}
{"action": "done", "result": "Successfully filled the form and clicked search"}
{"action": "fail", "reason": "CAPTCHA detected, human intervention needed"}

## Critical Rules
1. ALWAYS look at the screenshot carefully before acting. Describe what you see in your "reason".
2. Be PRECISE with coordinates. Click the CENTER of buttons/fields, not edges.
3. When you see a dropdown with multiple options, READ ALL OPTIONS and select the correct one.
4. If you see a cookie consent banner, dismiss it first.
5. If the page is loading, use wait(3).
6. After typing in an autocomplete field, use wait(2) for suggestions before clicking.
7. The screenshot resolution is 1920x1080. Coordinates must be within this range.
8. If you see a CAPTCHA or 2FA page, return fail().
9. NEVER repeat the same action more than twice. If something didn't work, try a different approach.
10. If a previous click didn't seem to change anything, your coordinates may be wrong — adjust them.
11. When looking at previous actions, if you see you already did something, do NOT do it again.
12. You are provided with a list of visible interactive elements and their exact center coordinates (x, y). When you want to click or focus on an element, look it up in the list and use its EXACT coordinates to ensure precision.
"""


class AIBrowserAgent:
    """
    Vision-based browser automation agent powered by Gemini.
    
    Usage:
        agent = AIBrowserAgent(page, api_key="your-gemini-key")
        result = await agent.execute_task(
            "Search for ocean freight rates from Singapore to Hamburg on Maersk"
        )
    """
    
    def __init__(
        self,
        page,
        api_key: str,
        model_name: str = "gemini-2.5-flash",
        screenshot_dir: Optional[str] = None,
        verbose: bool = True,
    ):
        if not HAS_GENAI:
            raise ImportError(
                "google-genai is required. Install it with: "
                "pip install google-genai"
            )
        
        self.page = page
        self.verbose = verbose
        self.model_name = model_name
        
        # Configure Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Screenshot storage for debugging
        self.screenshot_dir = screenshot_dir or os.path.join(
            os.path.dirname(__file__), "screenshots"
        )
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Action history for context
        self.history = []
        self.step_count = 0
        
        # Rate limiting
        self._last_call_time = 0
        self._min_interval = 1.0  # Min 1 second between API calls
    
    def _log(self, msg: str):
        if self.verbose:
            safe_msg = msg.encode("ascii", errors="replace").decode("ascii")
            print(f"[AI-AGENT] {safe_msg}")
    
    async def _take_screenshot(self) -> bytes:
        """Capture the current page as a PNG screenshot."""
        screenshot_bytes = await self.page.screenshot(type="png")
        
        filename = f"step_{self.step_count:03d}_{datetime.now().strftime('%H%M%S')}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        with open(filepath, "wb") as f:
            f.write(screenshot_bytes)
        self._log(f"Screenshot saved: {filepath}")
        
        return screenshot_bytes
    
    def _build_prompt(self, task: str, extra_context: str = "") -> str:
        """Build the prompt with task description and action history."""
        history_text = ""
        if self.history:
            recent = self.history[-10:]
            history_lines = []
            for h in recent:
                history_lines.append(
                    f"  Step {h['step']}: {h['action']} -- {h.get('reason', 'N/A')} --> {h.get('result', 'OK')}"
                )
            history_text = "\n\nYour previous actions:\n" + "\n".join(history_lines)
            history_text += "\n\nDo NOT repeat an action that already succeeded. Move to the next step."
        
        prompt = f"""Current task: {task}
You are on step {self.step_count + 1}.
{extra_context}
{history_text}

Look at the screenshot and decide ONE next action. Respond with a single JSON object only."""
        
        return prompt
    
    def _parse_action(self, response_text: str) -> dict:
        """Parse Gemini's response into an action dict."""
        text = response_text.strip()
        
        # Remove markdown code fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()
        
        # Find complete JSON object in the text
        json_match = re.search(r'\{[^{}]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing the whole thing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Handle truncated JSON — try to close it
        if text.startswith("{") and not text.endswith("}"):
            # Remove trailing comma if present
            truncated = text.rstrip(", \n\r\t")
            # Try adding closing brace
            try:
                fixed = truncated + '}'
                parsed = json.loads(fixed)
                self._log(f"Fixed truncated JSON: {fixed[:100]}")
                return parsed
            except json.JSONDecodeError:
                # Try adding a dummy value and closing brace
                try:
                    fixed = truncated + '""}' 
                    parsed = json.loads(fixed)
                    self._log(f"Fixed truncated JSON with dummy: {fixed[:100]}")
                    return parsed
                except json.JSONDecodeError:
                    pass
        
        # Extract action keyword from partial text as fallback
        action_match = re.search(r'"action"\s*:\s*"(\w+)"', text)
        if action_match:
            action = action_match.group(1).lower()
            self._log(f"Extracted partial action '{action}' from truncated response")
            if action == "wait":
                return {"action": "wait", "seconds": 3, "reason": "Waiting (recovered from truncated response)"}
            elif action == "click":
                x_match = re.search(r'"x"\s*:\s*(\d+)', text)
                y_match = re.search(r'"y"\s*:\s*(\d+)', text)
                if x_match and y_match:
                    return {"action": "click", "x": int(x_match.group(1)), "y": int(y_match.group(1)), "reason": "Click (recovered from truncated response)"}
            elif action == "done":
                return {"action": "done", "result": "Task completed (recovered from truncated response)"}
        
        # Last resort: don't fail the whole task, just wait and retry
        self._log(f"Could not parse response, defaulting to wait: {text[:200]}")
        return {"action": "wait", "seconds": 2, "reason": "Could not parse AI response, waiting to retry"}
    
    async def _call_gemini_with_retry(self, prompt: str, image_part, max_retries: int = 3) -> str:
        """Call Gemini API with exponential backoff retry."""
        # Rate limiting
        elapsed = time.time() - self._last_call_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        
        for attempt in range(max_retries):
            try:
                self._last_call_time = time.time()
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=SYSTEM_PROMPT),
                                types.Part.from_text(text=prompt),
                                image_part,
                            ],
                        )
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=4096,
                        thinking_config=types.ThinkingConfig(
                            thinking_budget=-1,
                        ),
                    ),
                )
                
                return response.text
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                    self._log(f"Rate limited (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                elif "503" in error_str or "UNAVAILABLE" in error_str:
                    wait_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                    self._log(f"Server unavailable (attempt {attempt+1}/{max_retries}), waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        
        raise Exception(f"Failed after {max_retries} retries")
    
    async def _execute_action(self, action: dict) -> str:
        """Execute a parsed action on the browser page."""
        action_type = action.get("action", "").lower()
        reason = action.get("reason", "")
        
        try:
            if action_type == "click":
                x = int(action.get("x", 0))
                y = int(action.get("y", 0))
                self._log(f"CLICK ({x}, {y}) -- {reason}")
                await self.page.mouse.click(x, y)
                await self.page.wait_for_timeout(800)
                return f"Clicked at ({x}, {y})"
            
            elif action_type == "type":
                text = action.get("text", "")
                self._log(f"TYPE '{text}' -- {reason}")
                for char in text:
                    await self.page.keyboard.type(char, delay=50 + (hash(char) % 80))
                await self.page.wait_for_timeout(500)
                return f"Typed '{text}'"
            
            elif action_type == "clear_and_type":
                text = action.get("text", "")
                self._log(f"CLEAR+TYPE '{text}' -- {reason}")
                await self.page.keyboard.press("Control+a")
                await self.page.wait_for_timeout(100)
                await self.page.keyboard.press("Backspace")
                await self.page.wait_for_timeout(200)
                for char in text:
                    await self.page.keyboard.type(char, delay=50 + (hash(char) % 80))
                await self.page.wait_for_timeout(500)
                return f"Cleared and typed '{text}'"
            
            elif action_type == "press":
                key = action.get("key", "Enter")
                self._log(f"PRESS '{key}' -- {reason}")
                await self.page.keyboard.press(key)
                await self.page.wait_for_timeout(500)
                return f"Pressed '{key}'"
            
            elif action_type == "scroll":
                direction = action.get("direction", "down")
                self._log(f"SCROLL {direction} -- {reason}")
                delta = -400 if direction == "up" else 400
                await self.page.mouse.wheel(0, delta)
                await self.page.wait_for_timeout(800)
                return f"Scrolled {direction}"
            
            elif action_type == "wait":
                seconds = min(int(action.get("seconds", 2)), 10)
                self._log(f"WAIT {seconds}s -- {reason}")
                await self.page.wait_for_timeout(seconds * 1000)
                return f"Waited {seconds}s"
            
            elif action_type == "done":
                result = action.get("result", "Task completed")
                self._log(f"DONE -- {result}")
                return f"DONE: {result}"
            
            elif action_type == "fail":
                fail_reason = action.get("reason", "Unknown failure")
                self._log(f"FAIL -- {fail_reason}")
                return f"FAIL: {fail_reason}"
            
            else:
                self._log(f"Unknown action type: {action_type}")
                return f"Unknown action: {action_type}"
                
        except Exception as e:
            self._log(f"Action execution error: {e}")
            return f"Error executing {action_type}: {str(e)}"
    
    def _detect_loop(self) -> bool:
        """Detect if the agent is stuck repeating the same action."""
        if len(self.history) < 3:
            return False
        
        last_3 = [h["action"] for h in self.history[-3:]]
        if len(set(last_3)) == 1:
            self._log("WARNING: Detected action loop! Same action repeated 3 times.")
            return True
        return False
        
    async def _get_interactive_elements_context(self) -> str:
        """Find all visible interactive elements and format them as a prompt guide."""
        selectors = ['button', 'input', 'select', 'textarea', '[role="button"]', 'a[href]', 'mc-option', '[role="option"]']
        elements = []
        
        try:
            viewport = self.page.viewport_size
            width = viewport['width'] if viewport else 1920
            height = viewport['height'] if viewport else 1080
        except Exception:
            width = 1920
            height = 1080
            
        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                count = await locator.count()
                for i in range(count):
                    loc = locator.nth(i)
                    if await loc.is_visible():
                        box = await loc.bounding_box()
                        if box and box['width'] > 0 and box['height'] > 0:
                            # Calculate center coordinates
                            x = int(box['x'] + box['width'] / 2)
                            y = int(box['y'] + box['height'] / 2)
                            
                            # Filter elements outside the visible viewport
                            if 0 <= x <= width and 0 <= y <= height:
                                tag = await loc.evaluate("el => el.tagName")
                                
                                # Get label/text/placeholder
                                label = ""
                                if tag == "INPUT":
                                    label = (await loc.get_attribute("placeholder")) or \
                                            (await loc.get_attribute("name")) or \
                                            (await loc.get_attribute("id")) or ""
                                else:
                                    label = await loc.inner_text()
                                    if not label:
                                        label = await loc.evaluate("el => el.textContent")
                                
                                # Clean label
                                label = label.replace("\n", " ").strip()[:80]
                                
                                # Fallback label helper for unnamed buttons/inputs
                                if not label and tag == "BUTTON":
                                    id_val = await loc.get_attribute("id")
                                    class_val = await loc.get_attribute("class")
                                    label = f"Unnamed Button (id={id_val}, class={class_val})"
                                
                                elements.append(f"- [{tag}] '{label}' at ({x}, {y}) [size {int(box['width'])}x{int(box['height'])}]")
            except Exception:
                pass
                
        if not elements:
            return "No visible interactive elements detected in DOM."
            
        return "Interactive elements on screen (use these EXACT coordinates for precise clicking):\n" + "\n".join(elements)
    
    async def execute_task(
        self,
        task: str,
        max_steps: int = 40,
        extra_context: str = "",
    ) -> dict:
        """
        Execute a browser automation task using vision-based AI.
        
        Args:
            task: Natural language description of what to do
            max_steps: Maximum number of actions before giving up
            extra_context: Additional context
            
        Returns:
            dict with keys: success (bool), result (str), steps (int), history (list)
        """
        self.history = []
        self.step_count = 0
        start_time = time.time()
        
        self._log(f"Starting task: {task}")
        self._log(f"Model: {self.model_name}")
        self._log(f"Max steps: {max_steps}")
        self._log("=" * 60)
        
        for step in range(max_steps):
            self.step_count = step
            
            # Check for loops
            if self._detect_loop():
                extra_context += "\n\nWARNING: You have been repeating the same action. Try something DIFFERENT. If a click didn't work, the coordinates were probably wrong. Look at the screenshot more carefully."
            
            try:
                # 1. Take screenshot
                screenshot_bytes = await self._take_screenshot()
                
                # 1.5 Extract interactive elements from DOM to assist vision
                elements_context = await self._get_interactive_elements_context()
                step_context = extra_context + "\n\n" + elements_context
                
                # 2. Build prompt
                prompt = self._build_prompt(task, step_context)
                
                # 3. Send to Gemini with retry
                self._log(f"Step {step + 1}: Querying Gemini...")
                
                image_part = types.Part.from_bytes(
                    data=screenshot_bytes,
                    mime_type="image/png",
                )
                
                response_text = await self._call_gemini_with_retry(prompt, image_part)
                self._log(f"Response: {response_text[:200]}")
                
                # 4. Parse action
                action = self._parse_action(response_text)
                action_type = action.get("action", "").lower()
                
                # 5. Execute action
                result = await self._execute_action(action)
                
                # 6. Record in history
                self.history.append({
                    "step": step + 1,
                    "action": f"{action_type}({json.dumps({k: v for k, v in action.items() if k not in ('action', 'reason')}, default=str)})",
                    "reason": action.get("reason", ""),
                    "result": result,
                })
                
                # 7. Check terminal states
                if action_type == "done":
                    elapsed = time.time() - start_time
                    self._log("=" * 60)
                    self._log(f"Task completed in {step + 1} steps ({elapsed:.1f}s)")
                    return {
                        "success": True,
                        "result": action.get("result", ""),
                        "steps": step + 1,
                        "elapsed_seconds": elapsed,
                        "history": self.history,
                    }
                
                if action_type == "fail":
                    elapsed = time.time() - start_time
                    self._log("=" * 60)
                    self._log(f"Task failed at step {step + 1} ({elapsed:.1f}s)")
                    return {
                        "success": False,
                        "result": action.get("reason", "Unknown failure"),
                        "steps": step + 1,
                        "elapsed_seconds": elapsed,
                        "history": self.history,
                    }
                
                # Brief pause between steps
                await self.page.wait_for_timeout(500)
                
            except Exception as e:
                self._log(f"Step {step + 1} error: {e}")
                traceback.print_exc()
                self.history.append({
                    "step": step + 1,
                    "action": "error",
                    "reason": str(e),
                    "result": f"Error: {e}",
                })
                await self.page.wait_for_timeout(3000)
        
        elapsed = time.time() - start_time
        self._log("=" * 60)
        self._log(f"Task timed out after {max_steps} steps ({elapsed:.1f}s)")
        return {
            "success": False,
            "result": f"Timed out after {max_steps} steps",
            "steps": max_steps,
            "elapsed_seconds": elapsed,
            "history": self.history,
        }
