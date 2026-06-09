"""
Repair Report — generates and saves diagnosis reports on Playwright selector failures.
"""
import os
import json

def generate_report(
    context: dict,
    observer_results: dict,
    repair_suggestion: dict
) -> dict:
    """
    Assembles a comprehensive repair report and writes it as JSON and Markdown
    inside the step's specific diagnostic folder.
    """
    diagnostics_dir = observer_results.get("diagnostics_dir")
    if not diagnostics_dir or not os.path.exists(diagnostics_dir):
        print("[Repair Report] Error: Diagnostics folder does not exist.")
        return {}
        
    report = {
        "carrier": context.get("carrier"),
        "step_name": context.get("step_name"),
        "url": context.get("url"),
        "original_selector": context.get("original_selector"),
        "error_message": context.get("error_message"),
        "expected_action": context.get("expected_action"),
        "screenshot_path": observer_results.get("screenshot"),
        "dom_path": observer_results.get("dom"),
        "suggested_selector": repair_suggestion.get("suggested_selector"),
        "reasoning": repair_suggestion.get("reasoning"),
        "risk_level": repair_suggestion.get("risk_level"),
        "status": "PENDING_REVIEW"
    }
    
    # Save as JSON
    json_path = os.path.join(diagnostics_dir, "repair_report.json")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print(f"[Repair Report] Saved JSON report to {json_path}")
    except Exception as je:
        print(f"[Repair Report] Error saving JSON report: {je}")
        
    # Save as Markdown
    md_path = os.path.join(diagnostics_dir, "repair_report.md")
    try:
        # Convert absolute paths to relative or file links for ease of viewing
        screenshot_url = f"file:///{report['screenshot_path'].replace(os.sep, '/')}" if report['screenshot_path'] else "N/A"
        
        md_content = f"""# Connector Failure & Repair Suggestion

## Overview
* **Carrier**: {report['carrier']}
* **Failed Step**: {report['step_name']}
* **Intended Action**: {report['expected_action']}
* **Page URL**: {report['url']}

## AI Diagnosis & Suggested Fix
* **Proposed Selector**: `{report['suggested_selector']}`
* **Risk Level**: **{report['risk_level']}**
* **Reasoning**: {report['reasoning']}

## Error details
* **Original Selector**: `{report['original_selector']}`
* **Playwright Error**: 
  ```
  {report['error_message']}
  ```

## Diagnostic Evidence
* **Screenshot**: [Link to Screenshot]({screenshot_url})
* **HTML DOM Snapshot**: [dom.html](file:///{report['dom_path'].replace(os.sep, '/') if report['dom_path'] else 'N/A'})
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[Repair Report] Saved Markdown report to {md_path}")
    except Exception as me:
        print(f"[Repair Report] Error saving Markdown report: {me}")
        
    return report
