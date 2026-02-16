"""
Batch Redesign Script for 360Library.com
Re-renders all existing HTML pages using the new templates.

Walks generated_pages/{domain}/{concept}/*.html, reads sibling .md,
and re-renders HTML with the new header/footer/sidebar design.

Also handles flat-structure domains (e.g., health) where files are
directly in the domain folder without concept subdirectories.
"""

import sys
import time
import re
from pathlib import Path

# Add parent to path so we can import project modules
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_pages import markdown_to_html, get_calculator_html, get_page_title, slugify
from templates import (
    SHARED_CSS, ARTICLE_CSS, ANGLE_DISPLAY,
    generate_header_html, generate_footer_html,
    generate_breadcrumb_html, generate_sidebar_html,
)

OUTPUT_DIR = Path(__file__).parent / "generated_pages"
SKIP_DIRS = {"index.html", "robots.txt", "CNAME"}

# Standard angle slugs
KNOWN_ANGLES = {
    "what-is", "how-it-works", "example-of", "types-of",
    "common-misconceptions-about", "what-affects-it",
    "what-it-depends-on", "vs",
}


def extract_md_content(md_path):
    """Read .md file and return body content (strip YAML front matter and trailing notes)."""
    text = md_path.read_text(encoding="utf-8")

    # Strip YAML front matter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].strip()

    # Strip leading H1 (we generate our own)
    lines = text.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    # Strip trailing evergreen note
    content = "\n".join(lines).strip()
    if content.endswith("*This is an evergreen reference page. Content is factual and timeless.*"):
        content = content[:-len("*This is an evergreen reference page. Content is factual and timeless.*")].strip()
    # Strip trailing ---
    if content.endswith("---"):
        content = content[:-3].strip()

    return content


def extract_title_from_md(md_path):
    """Extract title from YAML front matter."""
    text = md_path.read_text(encoding="utf-8")
    match = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def render_article_html(page_title, meta_desc, html_content, calculator_html,
                        domain_slug, concept_slug, angle_id, all_angles,
                        canonical_path=None):
    """Render a full article page with the new design."""
    header = generate_header_html(active_domain=domain_slug)
    footer = generate_footer_html()

    breadcrumb = ""
    sidebar = ""
    if domain_slug and concept_slug and angle_id:
        breadcrumb = generate_breadcrumb_html(domain_slug, concept_slug, angle_id)
    if domain_slug and concept_slug and angle_id and all_angles:
        sidebar = generate_sidebar_html(domain_slug, concept_slug, angle_id, all_angles)

    canonical_tag = ""
    if canonical_path:
        canonical_tag = f'\n    <link rel="canonical" href="https://360library.com/{canonical_path}">'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">{canonical_tag}
    <title>{page_title} - 360Library</title>
    <style>
{SHARED_CSS}
{ARTICLE_CSS}
    </style>
</head>
<body>
{header}

{breadcrumb}

<div class="article-wrapper">
    <main class="article-main">
        <article>
            <h1>{page_title}</h1>

            {calculator_html}

            {html_content}
        </article>
    </main>

    {sidebar}
</div>

{footer}
</body>
</html>
"""


def get_meta_desc(topic, page_title):
    """Generate a meta description based on the topic."""
    return f"A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions."


def process_structured_domains():
    """Process domains with concept subdirectories (economics, finance, life_obligations, math, science)."""
    count = 0
    errors = 0

    for domain_dir in sorted(OUTPUT_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_dir.name.endswith("_deprecated"):
            continue
        if domain_dir.name in SKIP_DIRS:
            continue

        domain_slug = domain_dir.name

        # Check if this is a structured domain (has concept subdirectories)
        concept_dirs = [d for d in domain_dir.iterdir() if d.is_dir()]
        if not concept_dirs:
            continue  # Skip flat domains, handled separately

        for concept_dir in sorted(concept_dirs):
            concept_slug = concept_dir.name

            # Collect all angle stems for this concept
            html_files = list(concept_dir.glob("*.html"))
            all_angles = [f.stem for f in html_files]

            for html_file in sorted(html_files):
                angle_id = html_file.stem
                md_file = html_file.with_suffix(".md")

                if not md_file.exists():
                    print(f"  SKIP (no .md): {html_file.relative_to(OUTPUT_DIR)}")
                    continue

                try:
                    # Extract content from markdown
                    content = extract_md_content(md_file)
                    page_title = extract_title_from_md(md_file) or get_page_title(f"{angle_id} {concept_slug}")

                    # Convert markdown to HTML
                    html_content = markdown_to_html(content)

                    # Check for calculator
                    topic = concept_slug.replace("-", " ")
                    calculator_html = get_calculator_html(topic) or ""

                    # Generate meta description
                    meta_desc = get_meta_desc(topic, page_title)

                    # Render new HTML
                    canonical = f"{domain_slug}/{concept_slug}/{angle_id}.html"
                    new_html = render_article_html(
                        page_title, meta_desc, html_content, calculator_html,
                        domain_slug, concept_slug, angle_id, all_angles,
                        canonical_path=canonical,
                    )

                    # Write back
                    html_file.write_text(new_html, encoding="utf-8")
                    count += 1

                    if count % 100 == 0:
                        print(f"  Progress: {count} pages re-rendered...")

                except Exception as e:
                    errors += 1
                    print(f"  ERROR: {html_file.relative_to(OUTPUT_DIR)}: {e}")

    return count, errors


def process_flat_domains():
    """Process domains with flat file structure (e.g., health)."""
    count = 0
    errors = 0

    for domain_dir in sorted(OUTPUT_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_dir.name.endswith("_deprecated"):
            continue
        if domain_dir.name in SKIP_DIRS:
            continue

        domain_slug = domain_dir.name

        # Check if this is a flat domain (no concept subdirectories)
        concept_dirs = [d for d in domain_dir.iterdir() if d.is_dir()]
        if concept_dirs:
            continue  # Skip structured domains, handled above

        html_files = list(domain_dir.glob("*.html"))
        if not html_files:
            continue

        print(f"Processing flat domain: {domain_slug} ({len(html_files)} files)")

        # Group files by concept for flat domains
        # In health, files like: arthritis.html, arthritis-vs.html,
        # common-misconceptions-about-arthritis.html
        # We need to figure out concept groupings

        # Build a mapping: concept -> list of (angle_id, html_file)
        concept_map = {}
        for html_file in html_files:
            stem = html_file.stem
            md_file = html_file.with_suffix(".md")
            if not md_file.exists():
                continue

            # Try to identify concept and angle from filename
            concept, angle = _parse_flat_filename(stem)
            if concept not in concept_map:
                concept_map[concept] = {}
            concept_map[concept][angle] = html_file

        # Now re-render each file with its concept group
        for concept, angle_files in sorted(concept_map.items()):
            all_angles = list(angle_files.keys())

            for angle_id, html_file in sorted(angle_files.items()):
                md_file = html_file.with_suffix(".md")

                try:
                    content = extract_md_content(md_file)
                    page_title = extract_title_from_md(md_file) or get_page_title(f"{angle_id} {concept}")

                    html_content = markdown_to_html(content)

                    topic = concept.replace("-", " ")
                    calculator_html = get_calculator_html(topic) or ""
                    meta_desc = get_meta_desc(topic, page_title)

                    # For flat domains, canonical uses the actual filename
                    canonical = f"{domain_slug}/{html_file.stem}.html"
                    new_html = render_article_html(
                        page_title, meta_desc, html_content, calculator_html,
                        domain_slug, concept, angle_id, all_angles,
                        canonical_path=canonical,
                    )

                    html_file.write_text(new_html, encoding="utf-8")
                    count += 1

                    if count % 100 == 0:
                        print(f"  Progress: {count} flat pages re-rendered...")

                except Exception as e:
                    errors += 1
                    print(f"  ERROR: {html_file.relative_to(OUTPUT_DIR)}: {e}")

    return count, errors


def _parse_flat_filename(stem):
    """Parse a flat-structure filename into (concept, angle).

    Examples:
        'arthritis'                             -> ('arthritis', 'what-is')
        'arthritis-vs'                          -> ('arthritis', 'vs')
        'common-misconceptions-about-arthritis' -> ('arthritis', 'common-misconceptions-about')
        'examples-of-arthritis'                 -> ('arthritis', 'example-of')
        'types-of-arthritis'                    -> ('arthritis', 'types-of')
        'how-does-arthritis-work'               -> ('arthritis', 'how-it-works')
        'what-affects-arthritis'                -> ('arthritis', 'what-affects-it')
        'what-arthritis-depends-on'             -> ('arthritis', 'what-it-depends-on')
    """
    # "how-does-{concept}-work"
    if stem.startswith("how-does-") and stem.endswith("-work"):
        return stem[len("how-does-"):-len("-work")], "how-it-works"

    # "what-{concept}-depends-on"
    if stem.startswith("what-") and stem.endswith("-depends-on"):
        return stem[len("what-"):-len("-depends-on")], "what-it-depends-on"

    # Simple prefix patterns (longest prefix first to avoid false matches)
    angle_prefixes = [
        ("common-misconceptions-about-", "common-misconceptions-about"),
        ("examples-of-", "example-of"),
        ("types-of-", "types-of"),
        ("what-affects-", "what-affects-it"),
    ]

    for prefix, angle in angle_prefixes:
        if stem.startswith(prefix):
            concept = stem[len(prefix):]
            if concept:
                return concept, angle

    # "{concept}-vs"
    if stem.endswith("-vs"):
        return stem[:-3], "vs"

    # No angle detected — it's a base concept page (what-is)
    return stem, "what-is"


def main():
    start = time.time()
    print("=" * 60)
    print("360Library Batch Redesign")
    print("=" * 60)

    # Count total HTML files first
    total_html = sum(1 for _ in OUTPUT_DIR.rglob("*.html")
                     if "_deprecated" not in str(_) and _.name != "index.html")
    print(f"Found {total_html} HTML files to process\n")

    print("Processing structured domains...")
    s_count, s_errors = process_structured_domains()
    print(f"  Structured: {s_count} rendered, {s_errors} errors\n")

    print("Processing flat domains...")
    f_count, f_errors = process_flat_domains()
    print(f"  Flat: {f_count} rendered, {f_errors} errors\n")

    total_count = s_count + f_count
    total_errors = s_errors + f_errors
    elapsed = time.time() - start

    print("=" * 60)
    print(f"DONE: {total_count} pages re-rendered in {elapsed:.1f}s")
    if total_errors:
        print(f"ERRORS: {total_errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
