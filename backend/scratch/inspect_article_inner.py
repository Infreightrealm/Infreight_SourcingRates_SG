import os
import re

html_path = "scratch/cma_results_page.html"
if not os.path.exists(html_path):
    html_path = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\cma_results_page.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Let's clean up script and style tags
html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

# Let's print out the full HTML between <article class="card-route-horizontal spot-on is-collapsed"> and its closing </article>
# to see the entire inner HTML of Article 1!
start_idx = html_content.find('class="card-route-horizontal spot-on is-collapsed"')
if start_idx != -1:
    # Go back to start of <article
    art_start = html_content.rfind('<article', 0, start_idx)
    art_end = html_content.find('</article>', art_start)
    if art_end != -1:
        art_end += len('</article>')
        art_html = html_content[art_start:art_end]
        print("--- ARTICLE HTML LENGTH:", len(art_html))
        # Print first 2000 chars of HTML
        print("\n--- FIRST 2000 CHARS OF ARTICLE HTML ---")
        print(art_html[:2000])
        # Print last 2000 chars of HTML
        print("\n--- LAST 2000 CHARS OF ARTICLE HTML ---")
        print(art_html[-2000:])
        
        # Let's write the entire article HTML to a scratch file so we can view/search it
        scratch_art_path = "scratch/article_1_full.html"
        with open(scratch_art_path, "w", encoding="utf-8") as f_art:
            f_art.write(art_html)
        print(f"\nEntire article HTML written to {scratch_art_path}")
else:
    print("Article class not found.")
