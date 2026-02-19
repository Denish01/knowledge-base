"""
Sitemap Generator for Knowledge Base
Crawls structured folders and generates sitemap.xml
"""

import json
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


TOOLS_HOMEPAGE_CSS = """
/* === Tools Showcase === */
.tools-showcase {
    max-width: 1200px;
    margin: 64px auto 0;
    padding: 0 24px;
}
.tools-showcase-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    padding-bottom: 12px;
    border-bottom: 2px solid #E5E7EB;
}
.tools-showcase-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #1F2937;
}
.tools-showcase-header .tools-view-all {
    font-size: 14px;
    font-weight: 600;
    color: #059669;
}
.tools-showcase-header .tools-view-all:hover { text-decoration: underline; }
.tools-cat-group { margin-bottom: 28px; }
.tools-cat-label {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
    padding-left: 2px;
}
.tools-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
}
.tool-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    text-decoration: none;
    color: #1F2937;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
    border-left: 3px solid var(--tool-color, #059669);
}
.tool-chip:hover {
    border-color: var(--tool-color, #059669);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
    text-decoration: none;
    color: #1F2937;
}
.tool-chip-icon { font-size: 20px; flex-shrink: 0; }
.tool-chip-text { min-width: 0; }
.tool-chip-title {
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.tool-chip-sub {
    display: block;
    font-size: 11px;
    color: #6B7280;
    margin-top: 4px;
    line-height: 1.4;
}
.tools-country-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
    margin-top: 12px;
}
.tool-country-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-left: 3px solid var(--tool-color, #059669);
    border-radius: 10px;
    padding: 16px;
}
.tool-country-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.tool-country-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #1F2937;
    text-decoration: none;
    display: block;
}
.tool-country-card-title:hover {
    color: #1B4D8E;
    text-decoration: underline;
}
.tool-country-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.tool-country-link {
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    background: #F3F4F6;
    color: #6B7280;
    text-decoration: none;
    transition: background 0.15s, color 0.15s;
}
.tool-country-link:hover {
    background: #ECFDF5;
    color: #059669;
    text-decoration: none;
}
@media (max-width: 768px) {
    .tools-row { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
    .tool-chip { padding: 10px 12px; }
    .tool-chip-title { font-size: 13px; }
}
"""

# Category icons for tool chips
_TOOL_CAT_ICONS = {
    "finance": "💰", "tax": "🏛️", "math": "🔢",
    "business": "📊", "health": "❤️", "conversion": "🔄",
}
_TOOL_CAT_COLORS = {
    "finance": "#059669", "tax": "#DC2626", "math": "#D97706",
    "business": "#7C3AED", "health": "#0891B2", "conversion": "#2563EB",
}


def _build_tools_homepage_section():
    """Build a custom tools showcase section for the homepage using tool_registry.json."""
    registry_path = Path(__file__).parent / "tool_registry.json"
    if not registry_path.exists():
        return ""

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    categories_meta = registry.get("categories", {})
    category_order = ["finance", "tax", "math", "business", "health", "conversion"]

    # Group standalone + country calculators by category
    by_category = {}
    for calc in registry.get("calculators", []):
        cat = calc["category"]
        by_category.setdefault(cat, []).append({
            "slug": calc["slug"],
            "title": calc["title"],
            "type": "standalone",
            "desc": calc.get("meta_description", ""),
        })
    for calc in registry.get("country_calculators", []):
        cat = calc["category"]
        by_category.setdefault(cat, []).append({
            "slug": calc["slug"],
            "title": calc["title_pattern"].replace(" — {Country}", ""),
            "type": "country",
            "countries": calc.get("countries", []),
        })

    # Count total tools
    total_tools = sum(len(tools) for tools in by_category.values())
    total_country_pages = sum(
        len(t.get("countries", []))
        for tools in by_category.values()
        for t in tools
        if t["type"] == "country"
    )

    # Build category groups
    groups_html = ""
    for cat_slug in category_order:
        if cat_slug not in by_category:
            continue
        cat_meta = categories_meta.get(cat_slug, {"name": cat_slug.title(), "icon": "", "color": "#666"})
        color = _TOOL_CAT_COLORS.get(cat_slug, "#059669")
        icon = _TOOL_CAT_ICONS.get(cat_slug, "🔧")
        tools = by_category[cat_slug]

        # Separate standalone tools from country-variant tools
        standalone_chips = ""
        country_chips = ""
        for tool in tools:
            slug = tool["slug"]
            title = tool["title"]
            short = title.replace(" Calculator", "").replace(" Converter", "")

            if tool["type"] == "country":
                country_links = ""
                for cs in tool.get("countries", []):
                    cn = cs.replace("-", " ").title()
                    country_links += f'<a href="/tools/{slug}/{cs}/" class="tool-country-link">{cn}</a>\n'
                country_chips += f"""      <div class="tool-country-card" style="--tool-color:{color}">
        <div class="tool-country-card-header">
          <span class="tool-chip-icon">{icon}</span>
          <div>
            <a href="/tools/{slug}/" class="tool-country-card-title">{short}</a>
            <span class="tool-chip-sub">{len(tool['countries'])} countries</span>
          </div>
        </div>
        <div class="tool-country-row">{country_links}</div>
      </div>
"""
            else:
                # Extract brief description from meta_description
                desc = tool.get("desc", "")
                # Strip "Free X calculator. " prefix to get the action part
                brief = desc
                if ". " in brief:
                    brief = brief.split(". ", 1)[1]
                # Truncate to ~60 chars
                if len(brief) > 65:
                    brief = brief[:62].rsplit(" ", 1)[0] + "..."
                sub_html = f'\n          <span class="tool-chip-sub">{brief}</span>' if brief else ""
                standalone_chips += f"""      <a href="/tools/{slug}/" class="tool-chip" style="--tool-color:{color}">
        <span class="tool-chip-icon">{icon}</span>
        <span class="tool-chip-text">
          <span class="tool-chip-title">{short}</span>{sub_html}
        </span>
      </a>
"""

        standalone_html = ""
        if standalone_chips:
            standalone_html = f'<div class="tools-row">\n{standalone_chips}      </div>'
        country_html = ""
        if country_chips:
            country_html = f'<div class="tools-country-grid">\n{country_chips}      </div>'

        groups_html += f"""    <div class="tools-cat-group">
      <div class="tools-cat-label" style="color:{color}">{cat_meta.get('icon', icon)} {cat_meta['name']}</div>
      {standalone_html}
      {country_html}
    </div>
"""

    return f"""<section class="tools-showcase" id="tools">
    <div class="tools-showcase-header">
      <h2>🛠️ Free Calculators &amp; Tools</h2>
      <a href="/tools/" class="tools-view-all">View all {total_tools} tools &rarr;</a>
    </div>
{groups_html}</section>
"""


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

    # Build domain cards (exclude tools — shown separately)
    domain_cards = ""
    for slug, concepts in pages_by_domain.items():
        if slug == "tools":
            continue
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

    # Build concept grids per domain (skip tools — handled separately)
    concept_sections = ""
    for slug, concepts in pages_by_domain.items():
        if slug == "tools":
            continue
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

    # Build tools showcase section from registry
    tools_section = _build_tools_homepage_section()

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
{TOOLS_HOMEPAGE_CSS}
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

{tools_section}

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
            if len(parts) == 2 and parts[0] == "tools":
                # Standalone tool page: /tools/slug/
                domain = "tools"
                concept = parts[1]
                angle = "index"
            elif len(parts) < 3:
                continue
            else:
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
