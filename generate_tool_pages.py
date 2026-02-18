"""
Tool Page Generator for 360Library.com
Generates standalone calculator tool pages at /tools/

Usage:
    python generate_tool_pages.py --generate-all [--count N]
    python generate_tool_pages.py --generate-country-variants [--count N]
    python generate_tool_pages.py --build-index
    python generate_tool_pages.py --rebuild-html
    python generate_tool_pages.py --generate-single <slug>
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_pages" / "tools"
REGISTRY_FILE = BASE_DIR / "tool_registry.json"
TOOL_CONTENT_DIR = BASE_DIR / "generated_pages" / "tools_content"

# Ensure output dirs exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TOOL_CONTENT_DIR.mkdir(parents=True, exist_ok=True)

# Import project modules
try:
    from config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

from calculators import get_calculator_by_key, CALCULATOR_STYLES
from templates import (
    SHARED_CSS, TOOL_CSS, TOOL_CATEGORY_COLORS,
    generate_header_html, generate_footer_html,
    generate_tool_breadcrumb_html, generate_tool_jsonld,
    generate_tool_sidebar_html, generate_tool_page_html,
    generate_og_tags,
)


def log(msg, level="INFO"):
    """Simple logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


# =============================================================================
# REGISTRY
# =============================================================================

def load_tool_registry():
    """Load tool_registry.json."""
    if not REGISTRY_FILE.exists():
        log(f"Registry not found: {REGISTRY_FILE}", "ERROR")
        sys.exit(1)
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


# =============================================================================
# AI CONTENT GENERATION
# =============================================================================

TOOL_CONTENT_PROMPT = """You are writing expert content to wrap a calculator tool on a financial education website.

The calculator is: {title}
Category: {category}

Write 500-700 words of content that will appear BELOW the calculator widget on the page. The calculator is already shown above — do NOT recreate it in your text.

Structure your content with these H2 sections:
## How to Use This Calculator
- 2-3 sentences explaining what each input means
- A worked example with specific numbers

## The Formula Behind It
- Show the actual formula/equation in plain text
- Explain each variable briefly

## Practical Examples
- 3 real-world scenarios with specific dollar amounts/numbers
- Show what the calculator would output for each

## Common Questions
- 4-5 Q&A pairs about the topic (use H3 for each question)

Rules:
- Write in plain, direct English. No filler phrases like "it's important to note" or "in today's world."
- Use specific numbers and examples throughout — never be vague.
- Write for someone who just wants to use the calculator and understand the results.
- Do NOT use phrases: "dive into", "leverage", "navigate", "it's worth noting", "key takeaways", "in conclusion"
- Do NOT add a title or H1 — the page already has one.
- Use markdown formatting (## for H2, ### for H3, **bold**, - bullet lists, | tables).
- Keep paragraphs short (2-3 sentences max).
"""

COUNTRY_TOOL_PROMPT = """You are writing expert content for a {title} tool page on a financial education website.

Country: {country_name}
Calculator type: {calculator_key}

Write 500-700 words that will appear BELOW the calculator. The calculator is already shown above.

Structure:
## How {country_name} {tax_type} Works
- Brief overview of the {country_name} system
- Current rates/brackets if applicable

## How to Use This Calculator
- What each input means for {country_name} specifically
- A worked example with realistic {country_name} numbers in local context

## Key {country_name} {tax_type} Rules
- 3-5 important rules specific to {country_name}
- Filing deadlines, exemptions, special cases

## Common Questions
- 4-5 Q&A pairs specific to {country_name} (use H3)

Rules:
- Use specific {country_name} numbers, thresholds, and tax years.
- Write in plain, direct English. No filler.
- Do NOT add a title/H1.
- Use markdown (## H2, ### H3, **bold**, bullets).
- Keep paragraphs short.
"""


def generate_with_groq(prompt, model="llama-3.3-70b-versatile"):
    """Generate content using Groq API."""
    if not OPENAI_SDK_AVAILABLE:
        raise Exception("OpenAI SDK not installed. Run: pip install openai")
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not configured")

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert educational content writer creating calculator tool pages."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def get_tool_prompt(calc_def):
    """Build the AI prompt for a calculator tool page."""
    return TOOL_CONTENT_PROMPT.format(
        title=calc_def["title"],
        category=calc_def["category"],
    )


def get_country_tool_prompt(calc_def, country_name):
    """Build the AI prompt for a country-specific calculator tool page."""
    title = calc_def["title_pattern"].replace("{Country}", country_name)
    tax_type = calc_def["slug"].replace("-", " ").replace("calculator", "").strip().title()
    return COUNTRY_TOOL_PROMPT.format(
        title=title,
        country_name=country_name,
        calculator_key=calc_def["calculator_key"],
        tax_type=tax_type,
    )


def generate_tool_content(calc_def, country_name=None):
    """Generate AI content for a tool page. Returns the raw markdown."""
    if country_name:
        prompt = get_country_tool_prompt(calc_def, country_name)
    else:
        prompt = get_tool_prompt(calc_def)

    log(f"  Generating content via Groq...")
    content = generate_with_groq(prompt)
    return content.strip()


# =============================================================================
# MARKDOWN TO HTML (simplified version for tool pages)
# =============================================================================

def markdown_to_html(content):
    """Convert markdown content to HTML for tool pages."""
    def bold(text):
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\\1</strong>', text)

    def inline_code(text):
        return re.sub(r'`(.+?)`', r'<code>\\1</code>', text)

    def process_inline(text):
        return inline_code(bold(text))

    lines = content.strip().split('\n')
    html_lines = []
    in_list = False
    in_ol = False
    in_table = False

    def close_list():
        nonlocal in_list, in_ol
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        if in_ol:
            html_lines.append('</ol>')
            in_ol = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if not in_table:
                close_list()
            continue

        # Headers
        if stripped.startswith('### '):
            close_list()
            text = stripped[4:]
            slug = re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))
            html_lines.append(f'<h3 id="{slug}">{process_inline(text)}</h3>')
            continue
        if stripped.startswith('## '):
            close_list()
            text = stripped[3:]
            slug = re.sub(r'[^a-z0-9-]', '', text.lower().replace(' ', '-'))
            html_lines.append(f'<h2 id="{slug}">{process_inline(text)}</h2>')
            continue

        # Table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            if '---' in stripped:
                continue  # Skip separator row
            if not in_table:
                close_list()
                in_table = True
                html_lines.append('<div class="table-wrapper"><table>')
                cells = [c.strip() for c in stripped.strip('|').split('|')]
                html_lines.append('<thead><tr>' + ''.join(f'<th>{process_inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            html_lines.append('<tr>' + ''.join(f'<td>{process_inline(c)}</td>' for c in cells) + '</tr>')
            continue
        if in_table:
            html_lines.append('</tbody></table></div>')
            in_table = False

        # Unordered list
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                close_list()
                in_list = True
                html_lines.append('<ul>')
            html_lines.append(f'<li>{process_inline(stripped[2:])}</li>')
            continue

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if ol_match:
            if not in_ol:
                close_list()
                in_ol = True
                html_lines.append('<ol>')
            html_lines.append(f'<li>{process_inline(ol_match.group(2))}</li>')
            continue

        # Paragraph
        close_list()
        html_lines.append(f'<p>{process_inline(stripped)}</p>')

    close_list()
    if in_table:
        html_lines.append('</tbody></table></div>')

    return '\n'.join(html_lines)


# =============================================================================
# PAGE BUILDING
# =============================================================================

def build_tool_html(calc_def, content_md, country=None, country_slug=None):
    """Build the full HTML page for a tool."""
    if country:
        title = calc_def["title_pattern"].replace("{Country}", country)
        meta_desc = calc_def.get("meta_description_pattern", "").replace("{Country}", country).replace("{country_adj}", country)
        slug = calc_def["slug"]
    else:
        title = calc_def["title"]
        meta_desc = calc_def["meta_description"]
        slug = calc_def["slug"]

    # Get calculator HTML
    calc_styles, calc_html = get_calculator_by_key(calc_def["calculator_key"])
    if not calc_html:
        log(f"  WARNING: No calculator found for key '{calc_def['calculator_key']}'", "WARN")
        calc_html = '<p>Calculator loading...</p>'

    # Convert content to HTML
    content_html = markdown_to_html(content_md)

    return generate_tool_page_html(
        title=title,
        meta_description=meta_desc,
        calculator_html=calc_html,
        calculator_styles=calc_styles or "",
        content_html=content_html,
        category=calc_def["category"],
        slug=slug,
        related_tools=calc_def.get("related_tools", []),
        related_knowledge=calc_def.get("related_knowledge", []),
        country=country_slug,
    )


def save_content_json(slug, content, country_slug=None):
    """Save generated content to JSON for rebuild-html without API calls."""
    key = f"{slug}_{country_slug}" if country_slug else slug
    data = {
        "slug": slug,
        "country": country_slug,
        "content": content,
        "generated_at": datetime.now().isoformat(),
    }
    path = TOOL_CONTENT_DIR / f"{key}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_content_json(slug, country_slug=None):
    """Load previously generated content."""
    key = f"{slug}_{country_slug}" if country_slug else slug
    path = TOOL_CONTENT_DIR / f"{key}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("content")
    return None


# =============================================================================
# GENERATION PIPELINE
# =============================================================================

def generate_tool_page(calc_def, force=False):
    """Generate a single tool page."""
    slug = calc_def["slug"]
    out_dir = OUTPUT_DIR / slug
    out_file = out_dir / "index.html"

    if out_file.exists() and not force:
        log(f"  Skipping {slug} (already exists)")
        return False

    log(f"Generating: {calc_def['title']}")

    # Check for cached content first
    content = load_content_json(slug)
    if not content:
        content = generate_tool_content(calc_def)
        save_content_json(slug, content)
        time.sleep(1)  # Rate limit

    html = build_tool_html(calc_def, content)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html, encoding="utf-8")
    log(f"  Written: {out_file}", "SUCCESS")
    return True


def generate_country_page(calc_def, country_slug, force=False):
    """Generate a country-specific tool page."""
    slug = calc_def["slug"]
    country_name = country_slug.replace("-", " ").title()
    out_dir = OUTPUT_DIR / slug / country_slug
    out_file = out_dir / "index.html"

    if out_file.exists() and not force:
        log(f"  Skipping {slug}/{country_slug} (already exists)")
        return False

    log(f"Generating: {calc_def['title_pattern'].replace('{Country}', country_name)}")

    content = load_content_json(slug, country_slug)
    if not content:
        content = generate_tool_content(calc_def, country_name)
        save_content_json(slug, content, country_slug)
        time.sleep(1)

    html = build_tool_html(calc_def, content, country=country_name, country_slug=country_slug)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html, encoding="utf-8")
    log(f"  Written: {out_file}", "SUCCESS")
    return True


def generate_all_tools(count=None, force=False):
    """Generate all standalone tool pages."""
    registry = load_tool_registry()
    calculators = registry.get("calculators", [])

    if count:
        calculators = calculators[:count]

    generated = 0
    skipped = 0
    for calc_def in calculators:
        if generate_tool_page(calc_def, force=force):
            generated += 1
        else:
            skipped += 1

    log(f"\nDone: {generated} generated, {skipped} skipped")
    return generated


def generate_country_variants(count=None, force=False):
    """Generate country-specific tool pages."""
    registry = load_tool_registry()
    country_calcs = registry.get("country_calculators", [])

    generated = 0
    skipped = 0
    total = 0

    for calc_def in country_calcs:
        countries = calc_def.get("countries", [])
        for country_slug in countries:
            total += 1
            if count and total > count:
                break
            if generate_country_page(calc_def, country_slug, force=force):
                generated += 1
            else:
                skipped += 1
        if count and total > count:
            break

    log(f"\nDone: {generated} generated, {skipped} skipped")
    return generated


def rebuild_html(count=None):
    """Rebuild HTML from stored content JSON (no API calls)."""
    registry = load_tool_registry()
    rebuilt = 0

    # Standalone tools
    for calc_def in registry.get("calculators", []):
        slug = calc_def["slug"]
        content = load_content_json(slug)
        if content:
            html = build_tool_html(calc_def, content)
            out_dir = OUTPUT_DIR / slug
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html, encoding="utf-8")
            rebuilt += 1
            log(f"  Rebuilt: {slug}")

    # Country variants
    for calc_def in registry.get("country_calculators", []):
        slug = calc_def["slug"]
        for country_slug in calc_def.get("countries", []):
            content = load_content_json(slug, country_slug)
            if content:
                country_name = country_slug.replace("-", " ").title()
                html = build_tool_html(calc_def, content, country=country_name, country_slug=country_slug)
                out_dir = OUTPUT_DIR / slug / country_slug
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "index.html").write_text(html, encoding="utf-8")
                rebuilt += 1
                log(f"  Rebuilt: {slug}/{country_slug}")

    log(f"\nRebuilt {rebuilt} pages (no API calls)")
    return rebuilt


# =============================================================================
# TOOLS INDEX PAGE
# =============================================================================

def build_tools_index():
    """Build the /tools/index.html landing page."""
    registry = load_tool_registry()
    categories_meta = registry.get("categories", {})

    # Group calculators by category
    by_category = {}
    for calc in registry.get("calculators", []):
        cat = calc["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(calc)

    # Add country calculators as a summary
    for calc in registry.get("country_calculators", []):
        cat = calc["category"]
        if cat not in by_category:
            by_category[cat] = []
        country_count = len(calc.get("countries", []))
        by_category[cat].append({
            "slug": calc["slug"],
            "title": calc["title_pattern"].replace(" — {Country}", ""),
            "meta_description": f"Available for {country_count} countries",
            "is_country": True,
            "countries": calc.get("countries", []),
        })

    # Build category sections
    category_sections = ""
    total_tools = 0
    category_order = ["finance", "tax", "math", "business", "health", "conversion"]

    for cat_slug in category_order:
        if cat_slug not in by_category:
            continue
        cat_meta = categories_meta.get(cat_slug, {"name": cat_slug.title(), "icon": "", "color": "#666"})
        tools = by_category[cat_slug]
        total_tools += len(tools)

        cards = ""
        for tool in tools:
            slug = tool["slug"]
            title = tool["title"]
            desc = tool.get("meta_description", "")
            color = TOOL_CATEGORY_COLORS.get(cat_slug, "#059669")

            if tool.get("is_country"):
                # Country calculator card with sub-links
                country_links = ""
                for cs in tool.get("countries", [])[:6]:
                    cn = cs.replace("-", " ").title()
                    country_links += f'<a href="/tools/{slug}/{cs}/" style="font-size:12px;color:#6B7280;margin-right:8px">{cn}</a> '
                cards += f"""      <a href="/tools/{slug}/" class="tool-index-card" style="--cat-color:{color}">
        <h3>{title}</h3>
        <p>{desc}</p>
        <div style="margin-top:8px">{country_links}</div>
      </a>
"""
            else:
                cards += f"""      <a href="/tools/{slug}/" class="tool-index-card" style="--cat-color:{color}">
        <h3>{title}</h3>
        <p>{desc}</p>
      </a>
"""

        category_sections += f"""    <div class="tools-category">
      <div class="tools-category-header">
        <h2>{cat_meta.get('icon', '')} {cat_meta['name']}</h2>
      </div>
      <div class="tools-grid">
{cards}      </div>
    </div>
"""

    header = generate_header_html(active_domain="tools")
    footer = generate_footer_html()
    og = generate_og_tags(
        "Free Online Calculators & Tools - 360Library",
        "Free online calculators for finance, tax, math, business, and health. Instant results, no signup required.",
        "https://360library.com/tools/",
        og_type="website"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Free online calculators for finance, tax, math, business, and health. Instant results, no signup required.">
    <link rel="canonical" href="https://360library.com/tools/">
    {og}
    <title>Free Online Calculators & Tools - 360Library</title>
    <style>
{SHARED_CSS}
{TOOL_CSS}
    </style>
</head>
<body>
{header}

<section class="tools-hero">
    <h1>Free Online Calculators</h1>
    <p>Instant-result tools for finance, taxes, math, business, and health. No signup, no ads. Just answers.</p>
</section>

<section class="tools-section">
{category_sections}
</section>

{footer}
</body>
</html>"""

    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(html, encoding="utf-8")
    log(f"Tools index written: {index_path}", "SUCCESS")
    log(f"Total tools listed: {total_tools}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate tool pages for 360Library")
    parser.add_argument("--generate-all", action="store_true", help="Generate all standalone tool pages")
    parser.add_argument("--generate-country-variants", action="store_true", help="Generate country-specific tool pages")
    parser.add_argument("--generate-single", type=str, help="Generate a single tool by slug")
    parser.add_argument("--build-index", action="store_true", help="Build the tools index page")
    parser.add_argument("--rebuild-html", action="store_true", help="Rebuild HTML from stored content (no API calls)")
    parser.add_argument("--count", type=int, default=None, help="Limit number of pages to generate")
    parser.add_argument("--force", action="store_true", help="Overwrite existing pages")
    args = parser.parse_args()

    if not any([args.generate_all, args.generate_country_variants, args.generate_single,
                args.build_index, args.rebuild_html]):
        parser.print_help()
        return

    if args.generate_all:
        generate_all_tools(count=args.count, force=args.force)

    if args.generate_country_variants:
        generate_country_variants(count=args.count, force=args.force)

    if args.generate_single:
        registry = load_tool_registry()
        calc_def = None
        for c in registry.get("calculators", []):
            if c["slug"] == args.generate_single:
                calc_def = c
                break
        if calc_def:
            generate_tool_page(calc_def, force=args.force)
        else:
            log(f"Calculator not found: {args.generate_single}", "ERROR")

    if args.rebuild_html:
        rebuild_html(count=args.count)

    if args.build_index:
        build_tools_index()


if __name__ == "__main__":
    main()
