"""
Sitemap Generator for Knowledge Base
Crawls structured folders and generates sitemap.xml
"""

import os
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from templates import (
    DOMAIN_META, SHARED_CSS, HOMEPAGE_CSS, FLAT_DOMAINS,
    generate_header_html, generate_footer_html,
    flat_angle_to_filename,
    generate_homepage_jsonld, generate_og_tags,
)

# Configuration
BASE_URL = "https://360library.com"
OUTPUT_DIR = Path(__file__).parent / "generated_pages"
SITEMAP_PATH = Path(__file__).parent / "generated_pages" / "sitemap.xml"

def _parse_flat_filename(stem):
    """Parse a flat-structure filename into (concept, angle_id).

    Health domain uses flat files like:
        arthritis.html              -> ('arthritis', 'what-is')
        arthritis-vs.html           -> ('arthritis', 'vs')
        common-misconceptions-about-arthritis.html -> ('arthritis', 'common-misconceptions-about')
        examples-of-arthritis.html  -> ('arthritis', 'example-of')
        types-of-arthritis.html     -> ('arthritis', 'types-of')
        how-does-arthritis-work.html -> ('arthritis', 'how-it-works')
        what-affects-arthritis.html -> ('arthritis', 'what-affects-it')
        what-arthritis-depends-on.html -> ('arthritis', 'what-it-depends-on')
    """
    # Angle prefixes (order matters — longest first to avoid partial matches)
    if stem.startswith("common-misconceptions-about-"):
        return stem[len("common-misconceptions-about-"):], "common-misconceptions-about"
    if stem.startswith("examples-of-"):
        return stem[len("examples-of-"):], "example-of"
    if stem.startswith("types-of-"):
        return stem[len("types-of-"):], "types-of"
    if stem.startswith("what-affects-"):
        return stem[len("what-affects-"):], "what-affects-it"

    # "how-does-{concept}-work"
    if stem.startswith("how-does-") and stem.endswith("-work"):
        return stem[len("how-does-"):-len("-work")], "how-it-works"

    # "what-{concept}-depends-on"
    if stem.startswith("what-") and stem.endswith("-depends-on"):
        return stem[len("what-"):-len("-depends-on")], "what-it-depends-on"

    # "{concept}-vs"
    if stem.endswith("-vs"):
        return stem[:-3], "vs"

    # Plain "{concept}" = what-is
    return stem, "what-is"


def get_tool_pages():
    """Crawl tools/ directory and collect tool page URLs."""
    pages = []
    tools_dir = OUTPUT_DIR / "tools"
    if not tools_dir.exists():
        return pages

    for item in sorted(tools_dir.iterdir()):
        if item.is_file() and item.name == "index.html":
            # Tools index page
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            pages.append({
                "url": "/tools/",
                "lastmod": mtime.strftime("%Y-%m-%d"),
                "priority": "0.95",
                "changefreq": "monthly",
            })
        elif item.is_dir():
            # Tool directory (e.g., compound-interest-calculator/)
            tool_index = item / "index.html"
            if tool_index.exists():
                mtime = datetime.fromtimestamp(tool_index.stat().st_mtime)
                pages.append({
                    "url": f"/tools/{item.name}/",
                    "lastmod": mtime.strftime("%Y-%m-%d"),
                    "priority": "0.9",
                    "changefreq": "monthly",
                })
            # Country subdirectories (e.g., income-tax-calculator/united-states/)
            for sub in sorted(item.iterdir()):
                if sub.is_dir():
                    sub_index = sub / "index.html"
                    if sub_index.exists():
                        mtime = datetime.fromtimestamp(sub_index.stat().st_mtime)
                        pages.append({
                            "url": f"/tools/{item.name}/{sub.name}/",
                            "lastmod": mtime.strftime("%Y-%m-%d"),
                            "priority": "0.8",
                            "changefreq": "monthly",
                        })

    return pages


def get_all_pages():
    """Crawl all domain folders and collect page URLs.

    Handles two directory layouts:
      - Structured: domain/concept/angle.html  (economics, finance, etc.)
      - Flat:       domain/filename.html        (health)
    """
    pages = []

    skip_names = {"index.html", "robots.txt", "CNAME", "tools", "tools_content"}
    for domain_dir in sorted(OUTPUT_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_dir.name.endswith("_deprecated"):
            continue
        if domain_dir.name in skip_names:
            continue

        domain_folder = domain_dir.name
        has_concept_dirs = any(d.is_dir() for d in domain_dir.iterdir())

        if has_concept_dirs:
            # --- Structured layout: domain/concept/angle.html ---
            for concept_dir in sorted(domain_dir.iterdir()):
                if not concept_dir.is_dir():
                    continue
                concept = concept_dir.name

                for html_file in concept_dir.glob("*.html"):
                    angle = html_file.stem
                    url_path = f"/{domain_folder}/{concept}/{angle}.html"
                    mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
                    lastmod = mtime.strftime("%Y-%m-%d")

                    pages.append({
                        "url": url_path,
                        "lastmod": lastmod,
                        "priority": get_priority(angle),
                        "changefreq": "monthly"
                    })
        else:
            # --- Flat layout: domain/filename.html ---
            for html_file in sorted(domain_dir.glob("*.html")):
                stem = html_file.stem
                concept, angle = _parse_flat_filename(stem)
                # URL uses the actual filename so the server can resolve it
                url_path = f"/{domain_folder}/{stem}.html"
                mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
                lastmod = mtime.strftime("%Y-%m-%d")

                pages.append({
                    "url": url_path,
                    "lastmod": lastmod,
                    "priority": get_priority(angle),
                    "changefreq": "monthly",
                    # Extra fields for flat pages so main() can group them
                    "_flat": True,
                    "_concept": concept,
                    "_angle": angle,
                })

    # Add tool pages
    pages.extend(get_tool_pages())

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
    today = datetime.now().strftime("%Y-%m-%d")
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{base_url}/</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]

    # Add legal/static pages
    for static_page in ["/privacy.html", "/terms.html"]:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{base_url}{static_page}</loc>")
        xml_lines.append(f"    <lastmod>{today}</lastmod>")
        xml_lines.append("    <changefreq>yearly</changefreq>")
        xml_lines.append("    <priority>0.3</priority>")
        xml_lines.append("  </url>")

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


def _flat_angle_to_filename(concept, angle):
    """Alias for shared flat_angle_to_filename."""
    return flat_angle_to_filename(concept, angle)


def generate_index_page(pages_by_domain, flat_domains=None):
    """Generate the redesigned index.html homepage."""
    if flat_domains is None:
        flat_domains = set()

    # Count totals
    total_pages = sum(
        len(angles) for concepts in pages_by_domain.values() for angles in concepts.values()
    )
    total_concepts = sum(len(concepts) for concepts in pages_by_domain.values())
    total_domains = len(pages_by_domain)

    # Build domain cards
    domain_cards = ""
    for slug, concepts in pages_by_domain.items():
        meta = DOMAIN_META.get(slug, {"name": slug.replace("_", " ").title(), "color": "#6B7280", "icon": "📄", "description": ""})
        concept_count = len(concepts)
        page_count = sum(len(a) for a in concepts.values())
        domain_cards += f"""      <div class="domain-card" style="--domain-color:{meta['color']}">
        <div class="domain-card-icon">{meta['icon']}</div>
        <h3>{meta['name']}</h3>
        <div class="card-meta">{concept_count} concepts &middot; {page_count} pages</div>
        <p>{meta['description']}</p>
        <a href="#{slug}" class="explore-link">Explore {meta['name']} &rarr;</a>
      </div>
"""

    # Build concept grids per domain
    concept_sections = ""
    for slug, concepts in pages_by_domain.items():
        meta = DOMAIN_META.get(slug, {"name": slug.replace("_", " ").title(), "color": "#6B7280", "icon": "📄"})
        concept_count = len(concepts)
        is_flat = slug in flat_domains

        cards = ""
        for concept, angles in sorted(concepts.items()):
            concept_title = concept.replace("-", " ").title()
            angle_tags = ""
            for angle in sorted(angles):
                from templates import ANGLE_DISPLAY
                angle_display = ANGLE_DISPLAY.get(angle, angle.replace("-", " ").title())
                if is_flat:
                    filename = _flat_angle_to_filename(concept, angle)
                    angle_tags += f'          <a href="/{slug}/{filename}.html" class="angle-link">{angle_display}</a>\n'
                else:
                    angle_tags += f'          <a href="/{slug}/{concept}/{angle}.html" class="angle-link">{angle_display}</a>\n'
            # "What Is" link for the concept heading
            if is_flat:
                main_href = f"/{slug}/{concept}.html"
            else:
                main_href = f"/{slug}/{concept}/what-is.html"
            cards += f"""      <div class="concept-card">
        <h3><a href="{main_href}">{concept_title}</a></h3>
        <div class="angle-links">
{angle_tags}        </div>
      </div>
"""

        concept_sections += f"""    <div class="domain-section" id="{slug}">
      <div class="domain-section-header">
        <h2>{meta['icon']} {meta['name']}</h2>
        <span class="badge" style="background:{meta['color']}">{concept_count} concepts</span>
      </div>
      <div class="concept-grid">
{cards}      </div>
    </div>
"""

    header = generate_header_html()
    footer = generate_footer_html()
    homepage_desc = "360Library — free encyclopedic reference covering economics, finance, health, life obligations, math, and science. Every concept explained from multiple angles."
    jsonld = generate_homepage_jsonld(total_pages, total_concepts, total_domains)
    og_tags = generate_og_tags("360Library — Learn Any Concept, Simply Explained", homepage_desc, "https://360library.com/", og_type="website")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{homepage_desc}">
    <link rel="canonical" href="https://360library.com/">
    {og_tags}
    <title>360Library — Learn Any Concept, Simply Explained</title>
    {jsonld}
    <style>
{SHARED_CSS}
{HOMEPAGE_CSS}
    </style>
</head>
<body>
{header}

<section class="hero">
    <h1>Learn Any Concept, Simply Explained</h1>
    <p>A free encyclopedic reference covering six knowledge domains. Every concept explored from multiple angles so you truly understand it.</p>
    <div class="hero-stats">
        <div class="hero-stat"><span class="num">{total_pages:,}</span><span class="label">Pages</span></div>
        <div class="hero-stat"><span class="num">{total_concepts:,}</span><span class="label">Concepts</span></div>
        <div class="hero-stat"><span class="num">{total_domains}</span><span class="label">Domains</span></div>
    </div>
</section>

<section class="domain-cards-section">
    <div class="domain-cards-grid">
{domain_cards}    </div>
</section>

<section class="concepts-section">
{concept_sections}</section>

{footer}
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
    flat_domains = set()
    for page in pages:
        if page.get("_flat"):
            # Flat-layout page — use pre-parsed concept/angle
            domain = page["url"].strip("/").split("/")[0]
            concept = page["_concept"]
            angle = page["_angle"]
            flat_domains.add(domain)
        else:
            # Structured-layout page — parse from URL
            parts = page["url"].strip("/").split("/")
            if len(parts) < 3:
                continue
            domain, concept, angle = parts[0], parts[1], parts[2]
            # Strip .html extension since we add it back when building links
            if angle.endswith(".html"):
                angle = angle[:-5]

        if domain not in pages_by_domain:
            pages_by_domain[domain] = {}
        if concept not in pages_by_domain[domain]:
            pages_by_domain[domain][concept] = []
        pages_by_domain[domain][concept].append(angle)

    # Generate index page
    index_html = generate_index_page(pages_by_domain, flat_domains=flat_domains)
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
