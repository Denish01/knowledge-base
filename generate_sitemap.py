"""
Sitemap Generator for Knowledge Base
Crawls structured folders and generates sitemap.xml
"""

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# Configuration
BASE_URL = "https://360library.com"
OUTPUT_DIR = Path(__file__).parent / "generated_pages"
SITEMAP_PATH = Path(__file__).parent / "sitemap.xml"

def get_all_pages():
    """Crawl all structured folders and collect page URLs."""
    pages = []

    # Find all *_structured directories
    for structured_dir in OUTPUT_DIR.glob("*_structured"):
        domain = structured_dir.name.replace("_structured", "")

        # Each concept folder
        for concept_dir in structured_dir.iterdir():
            if concept_dir.is_dir():
                concept = concept_dir.name

                # Each angle file
                for html_file in concept_dir.glob("*.html"):
                    angle = html_file.stem

                    # Build URL path
                    url_path = f"/{domain}/{concept}/{angle}"

                    # Get last modified time
                    mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
                    lastmod = mtime.strftime("%Y-%m-%d")

                    pages.append({
                        "url": url_path,
                        "lastmod": lastmod,
                        "priority": get_priority(angle),
                        "changefreq": "monthly"
                    })

    return pages


def get_priority(angle):
    """Assign priority based on angle type."""
    priorities = {
        "what-is": "1.0",           # Core definitions highest
        "how-it-works": "0.9",
        "example-of": "0.8",
        "common-misconceptions-about": "0.7",
        "what-affects-it": "0.6",
        "what-it-depends-on": "0.6",
        "types-of": "0.5",
        "vs": "0.5",
    }
    return priorities.get(angle, "0.5")


def generate_sitemap(pages, base_url):
    """Generate sitemap.xml content."""
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for page in pages:
        full_url = base_url.rstrip("/") + quote(page["url"])
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{full_url}</loc>")
        xml_lines.append(f"    <lastmod>{page['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{page['priority']}</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    return "\n".join(xml_lines)


def generate_index_page(pages_by_domain):
    """Generate a simple index.html for navigation."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Base Index</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a1a1a; }
        h2 { color: #2a2a2a; margin-top: 40px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .domain-stats { color: #666; font-size: 14px; }
        .concept-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
        .concept-card { background: #f8f9fa; border-radius: 8px; padding: 16px; }
        .concept-card h3 { margin: 0 0 8px 0; font-size: 16px; }
        .concept-card a { color: #1a73e8; text-decoration: none; font-size: 13px; display: block; margin: 4px 0; }
        .concept-card a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Knowledge Base</h1>
    <p>A structured knowledge index covering finance and life obligations.</p>
"""

    for domain, concepts in pages_by_domain.items():
        domain_title = domain.replace("_", " ").title()
        html += f"\n    <h2>{domain_title}</h2>\n"
        html += f"    <p class='domain-stats'>{len(concepts)} concepts</p>\n"
        html += "    <div class='concept-grid'>\n"

        for concept, angles in sorted(concepts.items()):
            concept_title = concept.replace("-", " ").title()
            html += f"      <div class='concept-card'>\n"
            html += f"        <h3>{concept_title}</h3>\n"
            for angle in sorted(angles):
                angle_display = angle.replace("-", " ").title()
                html += f"        <a href='/{domain}/{concept}/{angle}.html'>{angle_display}</a>\n"
            html += "      </div>\n"

        html += "    </div>\n"

    html += """
</body>
</html>"""

    return html


def main():
    print("Generating sitemap...")

    # Collect all pages
    pages = get_all_pages()
    print(f"Found {len(pages)} pages")

    # Generate sitemap
    sitemap_xml = generate_sitemap(pages, BASE_URL)
    SITEMAP_PATH.write_text(sitemap_xml, encoding="utf-8")
    print(f"Sitemap written to: {SITEMAP_PATH}")

    # Organize by domain and concept for index
    pages_by_domain = {}
    for page in pages:
        parts = page["url"].strip("/").split("/")
        if len(parts) >= 3:
            domain, concept, angle = parts[0], parts[1], parts[2]
            if domain not in pages_by_domain:
                pages_by_domain[domain] = {}
            if concept not in pages_by_domain[domain]:
                pages_by_domain[domain][concept] = []
            pages_by_domain[domain][concept].append(angle)

    # Generate index page
    index_html = generate_index_page(pages_by_domain)
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print(f"Index page written to: {index_path}")

    # Summary
    print("\n" + "=" * 50)
    print("SITEMAP SUMMARY")
    print("=" * 50)
    for domain, concepts in pages_by_domain.items():
        total_pages = sum(len(angles) for angles in concepts.values())
        print(f"  {domain}: {len(concepts)} concepts, {total_pages} pages")
    print(f"\nTotal: {len(pages)} pages")


if __name__ == "__main__":
    main()
