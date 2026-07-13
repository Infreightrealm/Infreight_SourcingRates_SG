# Admin Page & Port Prioritization Guide

This guide explains how to access the Admin Page, configure port prioritization (boosting), and verify changes with a live example.

---

## 🔒 How to Access the Admin Page

1. Open your Infreight Sourcing web application in your browser.
2. Click the **Lock Icon** (or "Admin Settings" button) located in the top-right corner of the header.
3. When prompted, enter the Admin Password:
   ```text
   brian_infreight
   ```
4. Click **Submit** to unlock the Admin Dashboard.

---

## ⚙️ How to Use Port Prioritization

Once logged in, you will see two configuration fields:

### 1. Popular Ports (UN/LOCODEs)
* **What it does**: Boosts specific individual ports to the very top of autocomplete suggestions.
* **Format**: A comma-separated list of 5-letter UN/LOCODEs.
* **Example**: `CNSHA, SGSIN, CNTXG, AUMEL`

### 2. Boosted Countries
* **What it does**: Boosts all ports belonging to specific countries, making them appear higher in searches.
* **Format**: A comma-separated list of 2-letter Country Codes.
* **Example**: `CN, IN, SG`

---

## 📝 Step-by-Step Example

Let's prioritize **Shanghai (CNSHA)** so it always displays first:

1. Access the Admin Page using the password `brian_infreight`.
2. Find the **Popular Ports** field and type: `CNSHA`
3. Click the **Save Configurations** button at the bottom of the page.
   * *The system will show a success notification.*
4. Go back to the main search page.
5. In the **Origin** or **Destination** input field, type: `Shan`
6. **Result**: **Shanghai, China (CNSHA)** will instantly appear at the very top of the suggestion dropdown, bypassing smaller or less relevant ports containing the letters "shan".

---

## ⚡ Important Notes
* **Instant Activation**: Changes saved on the Admin Page are applied **immediately**. You do **NOT** need to restart the server (no Ctrl+C) or run `git pull` on your laptop.
* **Permanence**: All configurations are saved locally on your laptop in the `backend/data/popular_ports_config.json` file. Because this file is listed in `.gitignore`, it is **100% permanent** and will never be overwritten or deleted by future Git updates.
