"""
Knowledge Page Generator
Self-propagating system that generates evergreen SEO text pages.

Features:
- Auto-generates pages from topics
- Embeds calculators where relevant
- Extracts related topics for expansion
- Auto-publishes via Git

Output: HTML/Markdown pages ready for publishing
Revenue: Ads, affiliates, licensing
"""

import json
import os
import re
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Try to import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Try to import config
try:
    from config import GOOGLE_API_KEY
except ImportError:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Import calculators
try:
    from calculators import get_calculator_html, get_calculator_for_topic
    CALCULATORS_AVAILABLE = True
except ImportError:
    CALCULATORS_AVAILABLE = False
    def get_calculator_html(topic): return None
    def get_calculator_for_topic(topic): return None

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_pages"
OUTPUT_DIR.mkdir(exist_ok=True)

TOPICS_FILE = BASE_DIR / "topics.json"
GENERATED_LOG = BASE_DIR / "generated_pages_log.json"
PENDING_TOPICS = BASE_DIR / "pending_topics.json"  # Topics discovered for future generation


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "[i]", "SUCCESS": "[+]", "ERROR": "[!]", "WARN": "[*]"}.get(level, "")
    print(f"[{timestamp}] {prefix} {message}")


# =============================================================================
# MASTER PROMPT - DO NOT CHANGE STRUCTURE
# =============================================================================

KNOWLEDGE_PAGE_PROMPT = """You are generating an evergreen educational reference page.

Topic: {topic}

Rules:
- Neutral, factual, timeless
- 8th-grade reading level
- No opinions, no dates, no trends, no current events
- No brand promotion or product recommendations
- No phrases like "in today's world" or "recently"

Structure (follow exactly):
1. ONE-SENTENCE DEFINITION: Start with "{{topic}} is..." or "{{topic}} refers to..."
2. SIMPLE EXPLANATION: 2-3 short paragraphs explaining the concept
3. KEY COMPONENTS: 4-6 bullet points of main principles or parts
4. COMMON MISCONCEPTIONS: 3-4 bullet points of things people get wrong
5. REAL-WORLD EXAMPLE: One concrete, simple example
6. SUMMARY: One sentence that captures the essence

Constraints:
- 600-800 words total
- Plain language, no jargon without explanation
- No emojis
- No markdown formatting (I will add it)
- Evergreen content only - must be valid for 10+ years"""


# =============================================================================
# COMPARISON PAGE PROMPT (X vs Y)
# =============================================================================

COMPARISON_PAGE_PROMPT = """You are generating an evergreen comparison page.

Compare: {topic}

Rules:
- Neutral, factual, no winner declared
- 8th-grade reading level
- No opinions, no recommendations
- No dates or trends

Structure (follow exactly):
1. INTRODUCTION: One paragraph explaining what both terms are and why people compare them
2. SIDE-BY-SIDE COMPARISON: A clear list comparing key aspects:
   - Definition of each
   - Key characteristics of each
   - When to use each
   - Pros and cons of each
3. KEY DIFFERENCES: 4-5 bullet points highlighting the main distinctions
4. KEY SIMILARITIES: 2-3 bullet points of what they share
5. SIMPLE EXAMPLE: One scenario showing when you'd choose each
6. SUMMARY: One sentence capturing the core difference

Constraints:
- 600-800 words total
- Balanced treatment (no bias toward either option)
- No emojis
- Evergreen content only"""


# =============================================================================
# CLASSIFICATION PAGE PROMPT (Types of X, Parts of X)
# =============================================================================

CLASSIFICATION_PAGE_PROMPT = """You are generating an evergreen classification/list page.

Topic: {topic}

Rules:
- Factual, structured, comprehensive
- 8th-grade reading level
- No opinions or rankings
- No dates or trends

Structure (follow exactly):
1. INTRODUCTION: One paragraph explaining what {topic} covers and why classification matters
2. MAIN CATEGORIES: List each type/part/stage with:
   - Name
   - Brief definition (1-2 sentences)
   - Key characteristics
   - Simple example
3. COMPARISON TABLE: Summarize differences between categories
4. HOW THEY RELATE: Brief explanation of how categories connect or differ
5. SUMMARY: One sentence capturing the classification system

Constraints:
- 600-900 words total
- Clear hierarchy and organization
- No emojis
- Evergreen content only"""


# =============================================================================
# TOPIC DATABASE
# =============================================================================

TOPIC_CATEGORIES = {
    "finance": [
        "compound interest",
        "exchange traded fund",
        "mutual fund",
        "dividend yield",
        "price to earnings ratio",
        "market capitalization",
        "bond yield",
        "inflation rate",
        "credit score",
        "mortgage amortization",
        "index fund",
        "asset allocation",
        "dollar cost averaging",
        "capital gains tax",
        "401k retirement plan",
        "roth ira",
        "traditional ira",
        "emergency fund",
        "net worth",
        "liquidity",
        "diversification",
        "risk tolerance",
        "annual percentage rate",
        "annual percentage yield",
        "amortization schedule",
    ],
    "science": [
        "photosynthesis",
        "cellular respiration",
        "water cycle",
        "carbon cycle",
        "nitrogen cycle",
        "rock cycle",
        "food chain",
        "food web",
        "ecosystem",
        "mitosis",
        "meiosis",
        "dna replication",
        "natural selection",
        "adaptation",
        "symbiosis",
        "decomposition",
        "evaporation",
        "condensation",
        "precipitation",
        "osmosis",
        "diffusion",
        "gravity",
        "friction",
        "kinetic energy",
        "potential energy",
    ],
    "math": [
        "prime numbers",
        "fractions",
        "decimals",
        "percentages",
        "ratios",
        "proportions",
        "mean median mode",
        "probability",
        "area of a circle",
        "perimeter",
        "volume",
        "pythagorean theorem",
        "order of operations",
        "exponents",
        "square roots",
        "absolute value",
        "integers",
        "variables",
        "linear equations",
        "slope",
        "coordinate plane",
        "greatest common factor",
        "least common multiple",
        "scientific notation",
        "standard deviation",
    ],
    "economics": [
        "supply and demand",
        "gross domestic product",
        "inflation",
        "deflation",
        "recession",
        "opportunity cost",
        "scarcity",
        "market equilibrium",
        "monopoly",
        "oligopoly",
        "perfect competition",
        "price elasticity",
        "fiscal policy",
        "monetary policy",
        "trade deficit",
        "trade surplus",
        "comparative advantage",
        "absolute advantage",
        "unemployment rate",
        "consumer price index",
        "interest rates",
        "central bank",
        "stock market",
        "bull market",
        "bear market",
    ],
    "biology": [
        "cell membrane",
        "cell wall",
        "nucleus",
        "mitochondria",
        "chloroplast",
        "ribosome",
        "protein synthesis",
        "enzyme",
        "hormone",
        "neuron",
        "synapse",
        "chromosome",
        "gene",
        "allele",
        "genotype",
        "phenotype",
        "dominant trait",
        "recessive trait",
        "heredity",
        "mutation",
        "biodiversity",
        "species",
        "population",
        "community",
        "biome",
    ],
    "language": [
        "noun",
        "verb",
        "adjective",
        "adverb",
        "pronoun",
        "preposition",
        "conjunction",
        "interjection",
        "subject and predicate",
        "sentence structure",
        "paragraph structure",
        "thesis statement",
        "topic sentence",
        "supporting details",
        "conclusion",
        "metaphor",
        "simile",
        "personification",
        "alliteration",
        "onomatopoeia",
        "hyperbole",
        "irony",
        "foreshadowing",
        "point of view",
        "narrative voice",
    ],
    "life_cycles": [
        "butterfly life cycle",
        "frog life cycle",
        "mosquito life cycle",
        "bee life cycle",
        "chicken life cycle",
        "plant life cycle",
        "salmon life cycle",
        "ladybug life cycle",
        "dragonfly life cycle",
        "grasshopper life cycle",
        "ant life cycle",
        "beetle life cycle",
        "starfish life cycle",
        "jellyfish life cycle",
        "turtle life cycle",
    ],

    # COMPARISON PAGES (X vs Y) - High intent, evergreen
    "comparisons": [
        "ETF vs mutual fund",
        "stocks vs bonds",
        "saving vs investing",
        "simple interest vs compound interest",
        "roth ira vs traditional ira",
        "debit card vs credit card",
        "fixed rate vs variable rate",
        "gross income vs net income",
        "assets vs liabilities",
        "bull market vs bear market",
        "mitosis vs meiosis",
        "dna vs rna",
        "plant cell vs animal cell",
        "aerobic vs anaerobic respiration",
        "photosynthesis vs cellular respiration",
        "weather vs climate",
        "speed vs velocity",
        "mass vs weight",
        "heat vs temperature",
        "element vs compound",
        "atom vs molecule",
        "acid vs base",
        "conductor vs insulator",
        "series circuit vs parallel circuit",
        "renewable vs nonrenewable energy",
        "mean vs median",
        "area vs perimeter",
        "radius vs diameter",
        "ratio vs proportion",
        "expression vs equation",
        "noun vs verb",
        "simile vs metaphor",
        "active voice vs passive voice",
        "fact vs opinion",
        "summary vs paraphrase",
        "democracy vs republic",
        "needs vs wants",
        "import vs export",
        "revenue vs profit",
        "inflation vs deflation",
    ],

    # CLASSIFICATION PAGES (Types of X, Parts of X)
    "classifications": [
        "types of ecosystems",
        "types of energy",
        "types of rocks",
        "types of clouds",
        "types of volcanoes",
        "types of plate boundaries",
        "types of chemical reactions",
        "types of waves",
        "types of muscles",
        "types of joints",
        "types of blood cells",
        "types of neurons",
        "types of investments",
        "types of bank accounts",
        "types of insurance",
        "types of taxes",
        "types of loans",
        "types of sentences",
        "types of triangles",
        "types of angles",
        "types of graphs",
        "types of fractions",
        "types of government",
        "types of economic systems",
        "parts of a cell",
        "parts of a plant",
        "parts of a flower",
        "parts of the brain",
        "parts of the heart",
        "parts of an atom",
        "parts of speech",
        "parts of a sentence",
        "stages of the water cycle",
        "stages of cellular respiration",
        "stages of mitosis",
        "stages of meiosis",
        "branches of government",
        "layers of the atmosphere",
        "layers of the earth",
        "levels of organization in biology",
    ],
}


def get_all_topics():
    """Get all topics from all categories."""
    all_topics = []
    for category, topics in TOPIC_CATEGORIES.items():
        for topic in topics:
            all_topics.append({"topic": topic, "category": category})
    return all_topics


def load_generated_log():
    """Load log of already generated pages."""
    if GENERATED_LOG.exists():
        return json.loads(GENERATED_LOG.read_text())
    return {"generated": [], "failed": []}


def save_generated_log(log_data):
    """Save generation log."""
    GENERATED_LOG.write_text(json.dumps(log_data, indent=2))


# =============================================================================
# TEXT GENERATION
# =============================================================================

def generate_with_gemini(topic):
    """Generate knowledge page content using Gemini."""
    prompt = get_prompt_for_topic(topic)
    return generate_with_gemini_prompt(prompt)


def generate_with_gemini_prompt(prompt):
    """Generate content using Gemini with a custom prompt."""
    if not GENAI_AVAILABLE:
        raise Exception("google-genai package not installed")

    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY not configured")

    client = genai.Client(api_key=GOOGLE_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",  # Text model, not image
        contents=prompt,
    )

    return response.text


def generate_with_requests(topic):
    """Generate using REST API (fallback)."""
    prompt = get_prompt_for_topic(topic)
    return generate_with_requests_prompt(prompt)


def generate_with_requests_prompt(prompt):
    """Generate content using REST API with a custom prompt."""
    import requests

    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY not configured")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(
        f"{url}?key={GOOGLE_API_KEY}",
        json=payload,
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    elif response.status_code == 429:
        raise Exception("Rate limit exceeded - wait and retry")
    else:
        raise Exception(f"API error: {response.status_code}")


def detect_page_type(topic):
    """Detect what type of page this topic needs."""
    topic_lower = topic.lower()

    # Comparison pages (X vs Y)
    if " vs " in topic_lower or " versus " in topic_lower:
        return "comparison"

    # Classification pages
    classification_keywords = [
        "types of", "kinds of", "parts of", "stages of",
        "layers of", "levels of", "branches of", "forms of"
    ]
    for keyword in classification_keywords:
        if topic_lower.startswith(keyword):
            return "classification"

    # Default: definition page
    return "definition"


def get_prompt_for_topic(topic):
    """Get the appropriate prompt template for a topic."""
    page_type = detect_page_type(topic)

    if page_type == "comparison":
        return COMPARISON_PAGE_PROMPT.format(topic=topic)
    elif page_type == "classification":
        return CLASSIFICATION_PAGE_PROMPT.format(topic=topic)
    else:
        return KNOWLEDGE_PAGE_PROMPT.format(topic=topic)


def generate_content(topic):
    """Generate page content using available method."""
    try:
        prompt = get_prompt_for_topic(topic)
        page_type = detect_page_type(topic)
        log(f"  Page type: {page_type}")

        if GENAI_AVAILABLE:
            return generate_with_gemini_prompt(prompt)
        else:
            return generate_with_requests_prompt(prompt)
    except Exception as e:
        log(f"Generation failed: {e}", "ERROR")
        raise


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def slugify(text):
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = slug.replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = "-".join(filter(None, slug.split("-")))  # Remove double dashes
    return slug


def format_as_markdown(topic, content):
    """Format content as Markdown."""
    slug = slugify(topic)

    md = f"""---
title: "What is {topic.title()}?"
slug: {slug}
description: "A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions."
date: {datetime.now().strftime("%Y-%m-%d")}
---

# What is {topic.title()}?

{content}

---

*This is an evergreen reference page. Content is factual and timeless.*
"""
    return md


def get_page_title(topic):
    """Generate appropriate title based on page type."""
    page_type = detect_page_type(topic)

    if page_type == "comparison":
        # "ETF vs Mutual Fund" -> "ETF vs Mutual Fund: Key Differences Explained"
        return f"{topic.title()}: Key Differences Explained"
    elif page_type == "classification":
        # "Types of Ecosystems" -> "Types of Ecosystems: Complete Guide"
        return f"{topic.title()}: Complete Guide"
    else:
        # "Compound Interest" -> "What is Compound Interest?"
        return f"What is {topic.title()}?"


def format_as_html(topic, content):
    """Format content as standalone HTML with embedded calculator if applicable."""
    slug = slugify(topic)
    page_title = get_page_title(topic)
    page_type = detect_page_type(topic)

    # Convert content paragraphs to HTML
    paragraphs = content.strip().split("\n\n")
    html_content = ""

    for para in paragraphs:
        para = para.strip()
        if para.startswith("- ") or para.startswith("• "):
            # It's a list
            items = [line.strip().lstrip("-•").strip() for line in para.split("\n") if line.strip()]
            html_content += "<ul>\n"
            for item in items:
                html_content += f"  <li>{item}</li>\n"
            html_content += "</ul>\n"
        elif para:
            html_content += f"<p>{para}</p>\n"

    # Get calculator if applicable
    calculator_html = get_calculator_html(topic) or ""
    if calculator_html:
        log(f"  Adding calculator for: {topic}", "SUCCESS")

    # Generate meta description based on page type
    if page_type == "comparison":
        meta_desc = f"Compare {topic} - key differences, similarities, and when to use each. Clear explanation with examples."
    elif page_type == "classification":
        meta_desc = f"Complete guide to {topic} - all categories explained with definitions and examples."
    else:
        meta_desc = f"A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions."

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <title>{page_title} - Simple Explanation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #1a1a1a; }}
        h2 {{ color: #2a2a2a; margin-top: 32px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        p {{ margin-bottom: 16px; }}
        .example {{ background: #f5f5f5; padding: 16px; border-radius: 8px; margin: 16px 0; }}
    </style>
</head>
<body>
    <article>
        <h1>{page_title}</h1>

        {calculator_html}

        {html_content}
    </article>
</body>
</html>
"""
    return html


def format_as_json(topic, content, category="general"):
    """Format as structured JSON for API/licensing."""
    slug = slugify(topic)

    data = {
        "slug": slug,
        "topic": topic,
        "title": f"What is {topic.title()}?",
        "category": category,
        "content": content,
        "meta_description": f"A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions.",
        "word_count": len(content.split()),
        "generated_date": datetime.now().isoformat(),
    }

    return json.dumps(data, indent=2)


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_knowledge_page(topic, category="general", output_formats=None):
    """
    Generate a complete knowledge page for a topic.

    Args:
        topic: The topic to explain
        category: Topic category for organization
        output_formats: List of formats to output (markdown, html, json)

    Returns:
        Dict with paths to generated files
    """
    if output_formats is None:
        output_formats = ["markdown", "html", "json"]

    log(f"Generating page for: {topic}")

    # Generate content
    content = generate_content(topic)

    if not content:
        raise Exception("No content generated")

    log(f"Generated {len(content.split())} words", "SUCCESS")

    # Create output files
    slug = slugify(topic)
    results = {"topic": topic, "slug": slug, "files": {}}

    # Create category subdirectory
    category_dir = OUTPUT_DIR / category
    category_dir.mkdir(exist_ok=True)

    if "markdown" in output_formats:
        md_content = format_as_markdown(topic, content)
        md_path = category_dir / f"{slug}.md"
        md_path.write_text(md_content, encoding="utf-8")
        results["files"]["markdown"] = str(md_path)
        log(f"  Saved: {md_path.name}")

    if "html" in output_formats:
        html_content = format_as_html(topic, content)
        html_path = category_dir / f"{slug}.html"
        html_path.write_text(html_content, encoding="utf-8")
        results["files"]["html"] = str(html_path)
        log(f"  Saved: {html_path.name}")

    if "json" in output_formats:
        json_content = format_as_json(topic, content, category)
        json_path = category_dir / f"{slug}.json"
        json_path.write_text(json_content, encoding="utf-8")
        results["files"]["json"] = str(json_path)
        log(f"  Saved: {json_path.name}")

    return results


def generate_batch(topics=None, category=None, count=10):
    """
    Generate multiple knowledge pages.

    Args:
        topics: List of topic strings, or None to use database
        category: Filter by category if using database
        count: Number of pages to generate

    Returns:
        List of results
    """
    log_data = load_generated_log()
    already_generated = set(log_data["generated"])

    # Get topics
    if topics:
        topic_list = [{"topic": t, "category": category or "general"} for t in topics]
    else:
        all_topics = get_all_topics()
        if category:
            all_topics = [t for t in all_topics if t["category"] == category]
        # Filter out already generated
        all_topics = [t for t in all_topics if t["topic"] not in already_generated]
        random.shuffle(all_topics)
        topic_list = all_topics[:count]

    if not topic_list:
        log("No topics to generate (all done or none found)", "WARN")
        return []

    log(f"Generating {len(topic_list)} knowledge pages...")
    print("=" * 60)

    results = []

    for i, topic_info in enumerate(topic_list, 1):
        topic = topic_info["topic"]
        cat = topic_info["category"]

        print(f"\n[{i}/{len(topic_list)}] {topic}")
        print("-" * 40)

        try:
            result = generate_knowledge_page(topic, category=cat)
            results.append(result)
            log_data["generated"].append(topic)

        except Exception as e:
            log(f"Failed: {e}", "ERROR")
            log_data["failed"].append({"topic": topic, "error": str(e)})

        # Save progress
        save_generated_log(log_data)

        # Rate limiting
        if i < len(topic_list):
            import time
            time.sleep(2)  # Be nice to the API

    print("\n" + "=" * 60)
    log(f"Generated {len(results)}/{len(topic_list)} pages", "SUCCESS")

    return results


# =============================================================================
# TOPIC EXPANSION (Self-Propagation)
# =============================================================================

def extract_related_topics(content):
    """
    Extract potential new topics from generated content.
    Looks for:
    - Terms in bold
    - Capitalized concepts
    - Referenced terms
    """
    related = set()

    # Find terms that look like concepts (capitalized phrases, bold terms)
    # Pattern: words that appear to be defined or referenced
    patterns = [
        r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # Two Capitalized Words
        r'"([^"]+)"',  # Quoted terms
        r'\*\*([^*]+)\*\*',  # Bold terms (markdown)
        r'<strong>([^<]+)</strong>',  # Bold terms (html)
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean and validate
            term = match.strip().lower()
            if len(term) > 3 and len(term) < 50 and term.count(' ') <= 4:
                related.add(term)

    return list(related)


def load_pending_topics():
    """Load topics discovered but not yet generated."""
    if PENDING_TOPICS.exists():
        return json.loads(PENDING_TOPICS.read_text())
    return []


def save_pending_topics(topics):
    """Save pending topics list."""
    # Remove duplicates
    unique = list(set(topics))
    PENDING_TOPICS.write_text(json.dumps(unique, indent=2))


def add_discovered_topics(new_topics, generated_log):
    """Add newly discovered topics to pending queue."""
    pending = load_pending_topics()
    already_generated = set(generated_log.get("generated", []))
    existing_pending = set(pending)

    # Get all known topics
    all_known = set()
    for topics in TOPIC_CATEGORIES.values():
        all_known.update(t.lower() for t in topics)

    added = 0
    for topic in new_topics:
        topic_lower = topic.lower()
        if (topic_lower not in already_generated and
            topic_lower not in existing_pending and
            topic_lower not in all_known):
            pending.append(topic_lower)
            added += 1

    if added > 0:
        save_pending_topics(pending)
        log(f"Discovered {added} new topics for future generation", "SUCCESS")

    return added


# =============================================================================
# AUTO-PUBLISH (Git-based)
# =============================================================================

def auto_publish(commit_message=None):
    """
    Auto-commit and push generated pages to Git.
    Requires Git to be configured in the output directory.
    """
    if commit_message is None:
        commit_message = f"Auto-generated knowledge pages - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    try:
        # Check if git is available
        result = subprocess.run(
            ["git", "status"],
            cwd=OUTPUT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            log("Git not initialized in output directory", "WARN")
            return False

        # Add all changes
        subprocess.run(["git", "add", "."], cwd=OUTPUT_DIR, check=True)

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=OUTPUT_DIR,
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            log("No changes to commit", "INFO")
            return True

        # Commit
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=OUTPUT_DIR,
            check=True
        )

        # Push
        subprocess.run(["git", "push"], cwd=OUTPUT_DIR, check=True)

        log("Auto-published to Git", "SUCCESS")
        return True

    except subprocess.CalledProcessError as e:
        log(f"Git operation failed: {e}", "ERROR")
        return False
    except FileNotFoundError:
        log("Git not installed", "WARN")
        return False


# =============================================================================
# SELF-PROPAGATING PIPELINE
# =============================================================================

def run_self_propagating(count=10, auto_publish_enabled=False):
    """
    Run the self-propagating pipeline:
    1. Generate pages from queue
    2. Extract related topics
    3. Add to pending queue
    4. Optionally auto-publish
    """
    log("Starting self-propagating pipeline...")
    print("=" * 60)

    log_data = load_generated_log()
    already_generated = set(log_data.get("generated", []))

    # Get topics: pending first, then from database
    pending = load_pending_topics()
    pending = [t for t in pending if t not in already_generated]

    if pending:
        log(f"Found {len(pending)} pending discovered topics")
        topic_list = [{"topic": t, "category": "discovered"} for t in pending[:count]]
    else:
        # Use database topics
        all_topics = get_all_topics()
        all_topics = [t for t in all_topics if t["topic"] not in already_generated]
        random.shuffle(all_topics)
        topic_list = all_topics[:count]

    if not topic_list:
        log("No topics to generate", "WARN")
        return []

    results = []
    all_discovered = []

    for i, topic_info in enumerate(topic_list, 1):
        topic = topic_info["topic"]
        cat = topic_info["category"]

        print(f"\n[{i}/{len(topic_list)}] {topic}")
        print("-" * 40)

        try:
            # Generate
            content = generate_content(topic)

            if content:
                # Extract related topics for future
                discovered = extract_related_topics(content)
                all_discovered.extend(discovered)

                # Save files
                result = generate_knowledge_page(topic, category=cat)
                results.append(result)
                log_data["generated"].append(topic)

                # Remove from pending if it was there
                pending = [t for t in pending if t != topic]

        except Exception as e:
            log(f"Failed: {e}", "ERROR")
            log_data.setdefault("failed", []).append({"topic": topic, "error": str(e)})

        save_generated_log(log_data)

        # Rate limiting
        if i < len(topic_list):
            import time
            time.sleep(2)

    # Save updated pending list
    save_pending_topics(pending)

    # Add discovered topics
    if all_discovered:
        add_discovered_topics(all_discovered, log_data)

    # Auto-publish if enabled
    if auto_publish_enabled and results:
        auto_publish()

    print("\n" + "=" * 60)
    log(f"Generated: {len(results)} pages", "SUCCESS")
    log(f"Discovered: {len(set(all_discovered))} potential new topics")

    return results


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Page Generator - Self-Propagating System")
    parser.add_argument("--topic", type=str, help="Single topic to generate")
    parser.add_argument("--category", type=str, help="Category to generate from")
    parser.add_argument("--count", type=int, default=5, help="Number of pages to generate")
    parser.add_argument("--list-topics", action="store_true", help="List all available topics")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--self-propagate", action="store_true", help="Run self-propagating mode")
    parser.add_argument("--auto-publish", action="store_true", help="Auto-commit and push to Git")
    parser.add_argument("--show-pending", action="store_true", help="Show pending discovered topics")
    parser.add_argument("--show-calculators", action="store_true", help="List topics with calculators")

    args = parser.parse_args()

    if args.list_categories:
        print("Available categories:")
        for cat, topics in TOPIC_CATEGORIES.items():
            print(f"  {cat}: {len(topics)} topics")
        print(f"\nTotal: {sum(len(t) for t in TOPIC_CATEGORIES.values())} topics")

    elif args.list_topics:
        for cat, topics in TOPIC_CATEGORIES.items():
            print(f"\n{cat.upper()}:")
            for topic in topics:
                calc = get_calculator_for_topic(topic)
                calc_mark = " [CALC]" if calc else ""
                print(f"  - {topic}{calc_mark}")

    elif args.show_pending:
        pending = load_pending_topics()
        print(f"Pending topics ({len(pending)}):")
        for topic in pending[:50]:
            print(f"  - {topic}")
        if len(pending) > 50:
            print(f"  ... and {len(pending) - 50} more")

    elif args.show_calculators:
        if CALCULATORS_AVAILABLE:
            from calculators import get_all_calculator_topics
            calc_topics = get_all_calculator_topics()
            print(f"Topics with calculators ({len(calc_topics)}):")
            for topic in calc_topics:
                print(f"  - {topic}")
        else:
            print("Calculators module not available")

    elif args.self_propagate:
        # Self-propagating mode
        results = run_self_propagating(
            count=args.count,
            auto_publish_enabled=args.auto_publish
        )
        print(f"\nTotal generated: {len(results)} pages")

    elif args.topic:
        # Single topic
        result = generate_knowledge_page(args.topic, category=args.category or "general")
        print(f"\nGenerated: {result['files']}")

    else:
        # Batch generation
        results = generate_batch(category=args.category, count=args.count)
        print(f"\nTotal generated: {len(results)} pages")
        print(f"Output directory: {OUTPUT_DIR}")
