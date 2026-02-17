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

try:
    from config import XAI_API_KEY
except ImportError:
    XAI_API_KEY = os.environ.get("XAI_API_KEY", "")

try:
    from config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Try to import OpenAI SDK (used for xAI Grok and Groq)
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

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
CANONICAL_CONCEPTS_DIR = BASE_DIR  # Where canonical_concepts_*.json files live
ANGLE_REGISTRY_FILE = BASE_DIR / "angle_registry.json"


def load_angle_registry():
    """Load the frozen angle registry."""
    if ANGLE_REGISTRY_FILE.exists():
        return json.loads(ANGLE_REGISTRY_FILE.read_text())
    return None


def get_canonical_slug(concept, angle_id):
    """
    Generate the canonical slug for a concept+angle pair.
    Uses the frozen angle registry - no positional prefixes allowed.
    """
    registry = load_angle_registry()
    if not registry:
        # Fallback to simple pattern
        return slugify(concept) if angle_id == "definition" else f"{angle_id}-{slugify(concept)}"

    angle_config = registry.get("angles", {}).get(angle_id)
    if not angle_config:
        return slugify(concept)

    pattern = angle_config.get("slug_pattern", "{concept}")
    return pattern.replace("{concept}", slugify(concept))


def get_canonical_title(concept, angle_id):
    """Generate the canonical title for a concept+angle pair."""
    registry = load_angle_registry()
    if not registry:
        return concept.title()

    angle_config = registry.get("angles", {}).get(angle_id)
    if not angle_config:
        return concept.title()

    pattern = angle_config.get("title_pattern", "{Concept}")
    return pattern.replace("{Concept}", concept.title())


def get_concept_completion_status(concept, category, generated_set=None):
    """
    Check completion status for a single concept.
    Checks the structured folder format: {category}_structured/{concept}/{angle}.json
    Returns dict with status per angle.
    """
    registry = load_angle_registry()
    if not registry:
        return {"error": "No angle registry found"}

    angles = registry.get("angles", {})
    concept_slug = slugify(concept)

    # Check structured folder
    structured_dir = OUTPUT_DIR / f"{category}_structured" / concept_slug

    status = {
        "concept": concept,
        "category": category,
        "angles": {},
        "required_complete": 0,
        "required_total": 0,
        "optional_complete": 0,
        "optional_total": 0,
        "is_complete": False,
    }

    for angle_id, angle_config in angles.items():
        is_required = angle_config.get("required", False)

        # Check if angle file exists in structured folder
        angle_file = structured_dir / f"{angle_id}.json"
        exists = angle_file.exists()

        status["angles"][angle_id] = {
            "slug": angle_id,
            "exists": exists,
            "required": is_required,
        }

        if is_required:
            status["required_total"] += 1
            if exists:
                status["required_complete"] += 1
        else:
            status["optional_total"] += 1
            if exists:
                status["optional_complete"] += 1

    # Concept is complete when all required angles exist
    status["is_complete"] = status["required_complete"] == status["required_total"]

    return status


def get_category_completion_report(category):
    """
    Generate a completion report for all concepts in a category.
    Uses the structured folder format: {category}_structured/{concept}/{angle}.json
    Shows exactly which concepts are missing which angles.
    """
    # Get concepts for this category
    concepts = TOPIC_CATEGORIES.get(category, [])
    if not concepts:
        return {"error": f"No concepts found for category: {category}"}

    report = {
        "category": category,
        "total_concepts": len(concepts),
        "complete_concepts": 0,
        "incomplete_concepts": [],
        "missing_angles_summary": {},
    }

    registry = load_angle_registry()
    if not registry:
        return {"error": "No angle registry found"}

    for concept in concepts:
        status = get_concept_completion_status(concept, category)

        if status["is_complete"]:
            report["complete_concepts"] += 1
        else:
            # Find missing required angles
            missing = []
            for angle_id, angle_status in status["angles"].items():
                if angle_status["required"] and not angle_status["exists"]:
                    missing.append(angle_id)
                    # Track summary
                    report["missing_angles_summary"][angle_id] = \
                        report["missing_angles_summary"].get(angle_id, 0) + 1

            report["incomplete_concepts"].append({
                "concept": concept,
                "missing_required": missing,
                "required_complete": status["required_complete"],
                "required_total": status["required_total"],
            })

    report["completion_percentage"] = (
        report["complete_concepts"] / report["total_concepts"] * 100
        if report["total_concepts"] > 0 else 0
    )

    return report


def load_canonical_concepts(domain):
    """
    Load the canonical concept list for a domain.
    These are the AUTHORITATIVE concepts for closure tracking.

    Returns: dict with concepts by subcategory, or None if not found
    """
    canonical_file = CANONICAL_CONCEPTS_DIR / f"canonical_concepts_{domain}.json"
    if canonical_file.exists():
        data = json.loads(canonical_file.read_text())
        return data
    return None


def get_canonical_concept_list(domain):
    """
    Get flat list of all canonical concepts for a domain.
    """
    data = load_canonical_concepts(domain)
    if not data:
        return []

    concepts = []
    for subcategory, concept_list in data.get("concepts", {}).items():
        concepts.extend(concept_list)

    return concepts


def get_domain_closure_status(domain):
    """
    Get closure status for a domain using canonical concepts.
    """
    canonical = load_canonical_concepts(domain)
    if not canonical:
        return {"error": f"No canonical concepts file for domain: {domain}"}

    concepts = get_canonical_concept_list(domain)
    log_data = load_generated_log()
    generated = set(g.lower() for g in log_data.get("generated", []))

    # Calculate coverage against canonical list
    covered = 0
    uncovered = []

    for concept in concepts:
        # Check if base or any angle exists
        if concept.lower() in generated:
            covered += 1
        else:
            # Check angles
            has_angle = False
            for pattern in CANONICAL_EXPANSIONS:
                expanded = pattern.format(topic=concept).lower()
                if expanded in generated:
                    has_angle = True
                    break
            if has_angle:
                covered += 1
            else:
                uncovered.append(concept)

    total = len(concepts)
    percentage = (covered / total * 100) if total > 0 else 0

    return {
        "domain": domain,
        "total_concepts": total,
        "covered": covered,
        "uncovered_count": len(uncovered),
        "percentage": percentage,
        "boundary": canonical.get("boundary", {}),
        "thresholds": canonical.get("closure_metrics", {}),
        "is_closed": percentage >= 98.0,
        "uncovered_sample": uncovered[:20],
    }


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
5. REAL-WORLD EXAMPLE: One concrete, simple example with specific numbers or names
6. SUMMARY: One sentence that captures the essence

Constraints:
- Start with a direct one-sentence answer before any sections
- 600-800 words total
- Plain language, no jargon without explanation
- No emojis
- No markdown formatting (I will add it)
- Evergreen content only - must be valid for 10+ years
- CRITICAL: Every paragraph must contain at least one specific fact, number, or named example. Never write a paragraph that only restates the topic name or gives vague generalities. No filler sentences. No repeating the same idea in different words. If a section would be vague, skip it and add depth to another section instead."""


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
- Start with a direct one-sentence answer before any sections
- 600-800 words total
- Balanced treatment (no bias toward either option)
- No emojis
- Evergreen content only
- CRITICAL: Every paragraph must contain at least one specific fact, number, or named example. No filler sentences. No repeating the same idea in different words."""


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
- Start with a direct one-sentence answer before any sections
- 600-900 words total
- Clear hierarchy and organization
- No emojis
- Evergreen content only
- CRITICAL: Every category must include a concrete, named example. No filler sentences. No repeating the same idea in different words."""


# =============================================================================
# QUESTION-FRAME PROMPTS (Upgrade 3: Question Templates)
# =============================================================================

HOW_IT_WORKS_PROMPT = """You are generating an evergreen "how it works" explanation page.

Topic: How {topic} works

Rules:
- Focus on mechanism, process, and steps
- 8th-grade reading level
- No opinions, no dates, no trends
- Explain cause and effect clearly

Structure (follow exactly):
1. QUICK ANSWER: 1-2 sentences explaining the core mechanism
2. STEP-BY-STEP PROCESS: Break down how it works into 4-6 clear steps
3. KEY COMPONENTS: What parts/elements are involved and their roles
4. VISUAL ANALOGY: One simple analogy that makes the mechanism intuitive
5. COMMON QUESTIONS: 3-4 "but what about..." questions people have
6. SUMMARY: One sentence capturing the essential mechanism

Constraints:
- Start with a direct one-sentence answer before any sections
- 500-700 words total
- Process-focused language (first, then, next, finally)
- No emojis
- Evergreen content only
- CRITICAL: Each step must explain a specific mechanism with cause and effect. No filler sentences. No repeating the same idea in different words. Include at least one concrete number or measurement."""


WHY_IT_MATTERS_PROMPT = """You are generating an evergreen "why it matters" explanation page.

Topic: Why {topic} matters

Rules:
- Focus on importance, impact, and relevance
- 8th-grade reading level
- No opinions, no dates, no trends
- Concrete benefits and consequences

Structure (follow exactly):
1. CORE IMPORTANCE: 1-2 sentences on why this concept matters
2. REAL-WORLD IMPACT: 3-4 ways this affects everyday life or decisions
3. WHAT HAPPENS WITHOUT IT: Consequences of ignoring or not understanding this
4. WHO NEEDS TO KNOW THIS: Groups of people for whom this is especially relevant
5. CONNECTION TO BIGGER PICTURE: How this fits into larger systems or concepts
6. SUMMARY: One sentence on the essential importance

Constraints:
- Start with a direct one-sentence answer before any sections
- 400-600 words total
- Benefit-focused language
- No emojis
- Evergreen content only
- CRITICAL: Every impact must cite a specific real-world consequence with numbers or named examples. No filler sentences. No repeating the same idea in different words."""


EXAMPLES_PROMPT = """You are generating an evergreen examples page.

Topic: Examples of {topic}

Rules:
- Focus on concrete, relatable examples
- 8th-grade reading level
- No opinions, no dates, no trends
- Variety of contexts and scales

Structure (follow exactly):
1. INTRODUCTION: Brief definition of {topic} to set context
2. EVERYDAY EXAMPLES: 3-4 examples from daily life everyone can relate to
3. NOTABLE EXAMPLES: 2-3 well-known or classic examples
4. EDGE CASES: 1-2 unusual or surprising examples that still qualify
5. NON-EXAMPLES: 2-3 things people often confuse for this but aren't
6. PATTERN: What do all valid examples have in common?

Constraints:
- Start with a direct one-sentence answer before any sections
- 500-700 words total
- Concrete and specific (names, numbers, scenarios)
- No emojis
- Evergreen content only
- CRITICAL: Every example must include a specific name, place, number, or measurement. Never describe an example vaguely. No filler sentences. No repeating the same idea in different words."""


MISCONCEPTIONS_PROMPT = """You are generating an evergreen misconceptions/myths page.

Topic: Common misconceptions about {topic}

Rules:
- Focus on what people get wrong and why
- 8th-grade reading level
- No opinions, no dates, no trends
- Respectful correction, not condescension

Structure (follow exactly):
1. INTRODUCTION: Why misconceptions about {topic} are common
2. MISCONCEPTION LIST: 5-7 common myths, each with:
   - The myth (what people believe)
   - The reality (what's actually true)
   - Why people believe this (the source of confusion)
3. HOW TO REMEMBER: Simple tips to avoid these mistakes
4. SUMMARY: The one thing to remember to avoid confusion

Constraints:
- Start with a direct one-sentence answer before any sections
- 500-700 words total
- "Myth vs Reality" format — each misconception MUST have all three parts (myth, reality, why people believe it). Do not list myths without realities.
- No emojis
- Evergreen content only
- CRITICAL: Each reality must cite a specific fact that disproves the myth. No filler sentences. No repeating the same idea in different words."""


BEGINNER_GUIDE_PROMPT = """You are generating an evergreen beginner's guide page.

Topic: {topic} for beginners

Rules:
- Assume zero prior knowledge
- 6th-grade reading level (simpler than usual)
- No jargon without immediate explanation
- Encouraging and accessible tone

Structure (follow exactly):
1. WHAT YOU'LL LEARN: 1-2 sentences on what this guide covers
2. THE BASICS: Simplest possible explanation of {topic}
3. KEY TERMS: 4-6 vocabulary words with plain definitions
4. FIRST STEPS: What a beginner should do or understand first
5. COMMON BEGINNER MISTAKES: 3-4 pitfalls to avoid
6. NEXT STEPS: What to learn after mastering the basics

Constraints:
- Start with a direct one-sentence answer before any sections
- 400-600 words total
- Short sentences, simple words
- No emojis
- Evergreen content only
- CRITICAL: Use a concrete analogy or everyday scenario in The Basics section. Each key term must have a specific, memorable definition — not a restatement of the term. No filler sentences."""


WHAT_AFFECTS_PROMPT = """You are generating an evergreen "what affects" explanation page.

Topic: What affects {topic}

Rules:
- Focus on factors, influences, and variables
- 8th-grade reading level
- No opinions, no dates, no trends
- Cause-and-effect relationships

Structure (follow exactly):
1. INTRODUCTION: Brief definition of {topic} and why understanding influences matters
2. MAIN FACTORS: 5-7 things that affect {topic}, each with:
   - The factor name
   - How it influences {topic}
   - Whether the effect is positive, negative, or variable
3. INTERCONNECTIONS: How these factors relate to each other
4. CONTROLLABLE VS UNCONTROLLABLE: Which factors can be managed
5. SUMMARY: The most important factors to understand

Constraints:
- Start with a direct one-sentence answer before any sections
- 500-700 words total
- Clear cause-effect language
- No emojis
- Evergreen content only
- CRITICAL: Each factor must explain the specific mechanism of influence (how exactly it affects the topic, with direction and magnitude). No filler sentences. No repeating the same idea in different words."""


WHAT_DEPENDS_ON_PROMPT = """You are generating an evergreen "what it depends on" explanation page.

Topic: What {topic} depends on

Rules:
- Focus on prerequisites, requirements, and foundations
- 8th-grade reading level
- No opinions, no dates, no trends
- Dependency relationships

Structure (follow exactly):
1. INTRODUCTION: Brief definition of {topic} and why dependencies matter
2. KEY DEPENDENCIES: 4-6 things {topic} requires or depends on, each with:
   - The dependency
   - Why it's necessary
   - What happens without it
3. ORDER OF IMPORTANCE: Which dependencies are most critical
4. COMMON GAPS: What people often overlook or assume
5. SUMMARY: The essential foundation for {topic}

Constraints:
- Start with a direct one-sentence answer before any sections
- 400-600 words total
- Prerequisite-focused language
- No emojis
- Evergreen content only
- CRITICAL: Each dependency must explain what specifically breaks or fails without it. No filler sentences. No repeating the same idea in different words."""


WHAT_USED_FOR_PROMPT = """You are generating an evergreen "what it's used for" explanation page.

Topic: What {topic} is used for

Rules:
- Focus on applications, purposes, and practical uses
- 8th-grade reading level
- No opinions, no dates, no trends
- Real-world applications

Structure (follow exactly):
1. INTRODUCTION: Brief definition of {topic} and its general purpose
2. PRIMARY USES: 3-4 main applications with concrete examples
3. SECONDARY USES: 2-3 less common but valid applications
4. WHO USES IT: Groups or fields that rely on {topic}
5. LIMITATIONS: What {topic} is NOT used for (to avoid confusion)
6. SUMMARY: The core purpose of {topic}

Constraints:
- Start with a direct one-sentence answer before any sections
- 500-700 words total
- Application-focused language
- No emojis
- Evergreen content only
- CRITICAL: Every use case must name a specific field, profession, or scenario where this is applied. No filler sentences. No repeating the same idea in different words."""


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
    "life_obligations": [
        # Tax obligations (8)
        "income tax",
        "tax filing",
        "tax withholding",
        "tax deduction",
        "tax credit",
        "estimated tax",
        "tax refund",
        "tax liability",
        # Insurance obligations (8)
        "health insurance",
        "auto insurance",
        "homeowners insurance",
        "renters insurance",
        "life insurance",
        "disability insurance",
        "insurance premium",
        "insurance deductible",
        # Debt obligations (8)
        "mortgage payment",
        "student loan",
        "credit card debt",
        "auto loan",
        "personal loan",
        "debt repayment",
        "minimum payment",
        "loan interest",
        # Retirement obligations (7)
        "retirement savings",
        "employer match",
        "retirement contribution",
        "required minimum distribution",
        "social security",
        "pension",
        "retirement withdrawal",
        # Legal obligations (7)
        "will",
        "power of attorney",
        "healthcare directive",
        "beneficiary designation",
        "estate planning",
        "probate",
        "guardianship",
        # Housing obligations (6)
        "rent payment",
        "property tax",
        "home maintenance",
        "utility bills",
        "homeowners association fees",
        "home inspection",
        # Family & Dependency (10)
        "dependent",
        "custodial parent",
        "noncustodial parent",
        "shared custody",
        "primary caregiver",
        "number of dependents",
        "household size",
        "cohabitation",
        "financial responsibility",
        "parental obligation",
        # Child Support (12)
        "child support",
        "child support obligation",
        "income shares model",
        "percentage of income model",
        "gross income for support",
        "net income for support",
        "support adjustment",
        "custody time adjustment",
        "child support duration",
        "support modification",
        "support deviation",
        "cost sharing",
        # Spousal Support (10)
        "spousal support",
        "alimony",
        "temporary support",
        "long-term support",
        "income disparity",
        "standard of living",
        "spousal support duration",
        "earning capacity",
        "self-sufficiency",
        "rehabilitative support",
        # Government Benefits (12)
        "government benefits",
        "income eligibility",
        "means testing",
        "benefit threshold",
        "benefit phaseout",
        "household income",
        "dependent qualification",
        "benefit reduction",
        "assistance programs",
        "public assistance",
        "benefit estimation",
        "eligibility criteria",
        # Payment Mechanics (8)
        "payment obligation",
        "payment schedule",
        "shared expenses",
        "proportional contribution",
        "income adjustment",
        "obligation estimate",
        "affordability assessment",
        "financial burden",
        # Employment obligations (6)
        "employment contract",
        "non-compete agreement",
        "direct deposit",
        "pay stub",
        "benefits enrollment",
        "open enrollment",
        # Family Budget (3)
        "dependent care",
        "education funding",
        "family budget",
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


# =============================================================================
# AUTO-LOAD CANONICAL CONCEPTS (Bridge self-expansion → page generation)
# =============================================================================
# Load topics from canonical_concepts_*.json for domains not hardcoded above.
# This allows domain_discovery.py to create new domains that knowledge_pages.py
# can immediately generate pages for.

def _load_canonical_concepts_into_categories():
    """Load canonical concept files and add missing domains to TOPIC_CATEGORIES."""
    import glob as glob_module
    pattern = str(BASE_DIR / "canonical_concepts_*.json")
    for filepath in glob_module.glob(pattern):
        path = Path(filepath)
        # Extract domain name: canonical_concepts_health.json -> health
        domain = path.stem.replace("canonical_concepts_", "")
        if domain in TOPIC_CATEGORIES:
            continue  # Already hardcoded, skip
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Flatten all subcategory concepts into a single list
            topics = []
            for subcategory, concepts in data.get("subcategories", {}).items():
                for concept in concepts:
                    # Use title (human-readable) and convert to lowercase
                    title = concept.get("title", concept.get("concept", ""))
                    if title:
                        topics.append(title.lower())
            if topics:
                TOPIC_CATEGORIES[domain] = topics
                log(f"Loaded {len(topics)} concepts for '{domain}' from {path.name}")
        except Exception as e:
            log(f"Failed to load {path.name}: {e}", "ERROR")

_load_canonical_concepts_into_categories()


# =============================================================================
# CANONICAL EXPANSION ENGINE (Upgrade 1)
# =============================================================================
# Turn one topic into 12 pages covering every canonical angle
# Based on: How humans naturally ask questions about any concept

CANONICAL_EXPANSIONS = [
    # 1. Base definition (what is X)
    "{topic}",

    # 2-4. Core understanding angles
    "how does {topic} work",           # Mechanism
    "why {topic} matters",             # Importance
    "examples of {topic}",             # Concrete illustrations

    # 5-7. Structure angles (some concepts won't have all 3)
    "parts of {topic}",                # Components
    "stages of {topic}",               # Process/sequence
    "types of {topic}",                # Categories

    # 8-10. Relationship angles
    "what affects {topic}",            # Influences
    "what {topic} depends on",         # Prerequisites
    "what {topic} is used for",        # Applications

    # 11-12. Clarification angles
    "common misconceptions about {topic}",  # Myth-busting
    "{topic} for beginners",           # Entry-level guide
]

# The 12 Canonical Angles (for reference and completeness tracking)
CANONICAL_ANGLES = [
    "definition",      # What is X
    "how",             # How does X work
    "why",             # Why does X matter
    "examples",        # Examples of X
    "parts",           # Parts of X
    "stages",          # Stages of X
    "types",           # Types of X
    "affects",         # What affects X
    "depends",         # What X depends on
    "used_for",        # What X is used for
    "misconceptions",  # Common misconceptions about X
    "beginner",        # X for beginners
]

# Map expansion patterns to their prompt/angle types
EXPANSION_TO_PROMPT_TYPE = {
    "how does {topic} work": "how",
    "why {topic} matters": "why",
    "examples of {topic}": "examples",
    "parts of {topic}": "parts",
    "stages of {topic}": "stages",
    "types of {topic}": "types",
    "what affects {topic}": "affects",
    "what {topic} depends on": "depends",
    "what {topic} is used for": "used_for",
    "common misconceptions about {topic}": "misconceptions",
    "{topic} for beginners": "beginner",
}

# Reverse mapping: angle ID to human-readable topic pattern
EXPANSION_TO_PATTERN = {
    # Old angle IDs (for backwards compatibility)
    "definition": "{topic}",
    "how": "how does {topic} work",
    "why": "why {topic} matters",
    "examples": "examples of {topic}",
    "parts": "parts of {topic}",
    "stages": "stages of {topic}",
    "types": "types of {topic}",
    "affects": "what affects {topic}",
    "depends": "what {topic} depends on",
    "used_for": "what {topic} is used for",
    "misconceptions": "common misconceptions about {topic}",
    "beginner": "{topic} for beginners",
    # New canonical angle IDs (from angle_registry.json)
    "what-is": "{topic}",
    "how-it-works": "how does {topic} work",
    "what-it-depends-on": "what {topic} depends on",
    "what-affects-it": "what affects {topic}",
    "types-of": "types of {topic}",
    "example-of": "examples of {topic}",
    "common-misconceptions-about": "common misconceptions about {topic}",
    "vs": "{topic} vs",
}

# Canonical title patterns per angle (for H1 and page title)
ANGLE_TO_TITLE = {
    "what-is": "What Is {Topic}?",
    "how-it-works": "How {Topic} Works",
    "what-it-depends-on": "What {Topic} Depends On",
    "what-affects-it": "What Affects {Topic}",
    "types-of": "Types of {Topic}",
    "example-of": "Example of {Topic}",
    "common-misconceptions-about": "Common Misconceptions About {Topic}",
    "vs": "{Topic} Compared",
}


def get_angle_title(concept, angle_id):
    """Get the canonical title for a concept+angle pair."""
    pattern = ANGLE_TO_TITLE.get(angle_id, "What Is {Topic}?")
    return pattern.replace("{Topic}", concept.replace("-", " ").title())

# Which angles are optional (not all concepts have these)
OPTIONAL_ANGLES = {"parts", "stages", "types"}


def expand_topic_to_angles(topic):
    """
    Explode one topic into multiple canonical angles.

    Example: "compound interest" becomes:
    - compound interest (definition)
    - how does compound interest work
    - why compound interest matters
    - examples of compound interest
    - common misconceptions about compound interest
    - compound interest for beginners

    Returns list of expanded topic strings.
    """
    expanded = []
    for pattern in CANONICAL_EXPANSIONS:
        expanded_topic = pattern.format(topic=topic)
        expanded.append(expanded_topic)
    return expanded


def get_all_expanded_topics(categories=None):
    """
    Get all topics expanded into all canonical angles.
    Uses the frozen angle registry for canonical naming.

    Args:
        categories: List of category names to expand, or None for all

    Returns:
        List of {"topic": str, "base_topic": str, "category": str, "angle": str, "canonical_slug": str}
    """
    all_expanded = []

    # Try to use the angle registry for canonical slugs
    registry = load_angle_registry()
    angles_from_registry = registry.get("angles", {}) if registry else {}

    for category, topics in TOPIC_CATEGORIES.items():
        # Skip comparison/classification - they have their own formats
        if category in ["comparisons", "classifications"]:
            continue
        if categories and category not in categories:
            continue

        for base_topic in topics:
            # If we have a registry, use it for canonical expansion
            if angles_from_registry:
                for angle_id, angle_config in angles_from_registry.items():
                    # Generate display topic (human-readable)
                    pattern = EXPANSION_TO_PATTERN.get(angle_id, "{topic}")
                    expanded_topic = pattern.format(topic=base_topic)

                    # Generate canonical slug (machine-readable, no a-b-c prefixes)
                    canonical_slug = get_canonical_slug(base_topic, angle_id)

                    all_expanded.append({
                        "topic": expanded_topic,
                        "base_topic": base_topic,
                        "category": category,
                        "angle": angle_id,
                        "canonical_slug": canonical_slug,
                        "required": angle_config.get("required", False),
                    })
            else:
                # Fallback to old pattern-based expansion
                for pattern in CANONICAL_EXPANSIONS:
                    expanded_topic = pattern.format(topic=base_topic)

                    # Determine the angle type
                    if pattern == "{topic}":
                        angle = "definition"
                    else:
                        angle = EXPANSION_TO_PROMPT_TYPE.get(pattern, "definition")

                    all_expanded.append({
                        "topic": expanded_topic,
                        "base_topic": base_topic,
                        "category": category,
                        "angle": angle,
                        "canonical_slug": slugify(expanded_topic),
                    })

    # Also include comparisons and classifications as-is
    for category in ["comparisons", "classifications"]:
        if categories and category not in categories:
            continue
        for topic in TOPIC_CATEGORIES.get(category, []):
            all_expanded.append({
                "topic": topic,
                "base_topic": topic,
                "category": category,
                "angle": "comparison" if category == "comparisons" else "classification",
            })

    return all_expanded


def count_expanded_topics():
    """Count total pages possible with canonical expansion."""
    expanded = get_all_expanded_topics()
    return len(expanded)


# =============================================================================
# CONCEPT GRAPH (Upgrade 2)
# =============================================================================
# Track relationships: parents, children, related, comparisons

CONCEPT_GRAPH_FILE = BASE_DIR / "concept_graph.json"


def load_concept_graph():
    """Load the concept graph from file."""
    if CONCEPT_GRAPH_FILE.exists():
        return json.loads(CONCEPT_GRAPH_FILE.read_text())
    return {}


def save_concept_graph(graph):
    """Save the concept graph to file."""
    CONCEPT_GRAPH_FILE.write_text(json.dumps(graph, indent=2))


def add_concept_to_graph(concept, parents=None, children=None, related=None, comparisons=None):
    """
    Add or update a concept in the graph.

    Args:
        concept: The concept name (lowercase)
        parents: List of parent/broader concepts
        children: List of child/narrower concepts
        related: List of related concepts (not hierarchical)
        comparisons: List of concepts commonly compared with this one
    """
    graph = load_concept_graph()

    concept_lower = concept.lower()

    if concept_lower not in graph:
        graph[concept_lower] = {
            "parents": [],
            "children": [],
            "related": [],
            "comparisons": [],
        }

    # Merge new relationships (avoid duplicates)
    if parents:
        graph[concept_lower]["parents"] = list(set(graph[concept_lower]["parents"] + [p.lower() for p in parents]))
    if children:
        graph[concept_lower]["children"] = list(set(graph[concept_lower]["children"] + [c.lower() for c in children]))
    if related:
        graph[concept_lower]["related"] = list(set(graph[concept_lower]["related"] + [r.lower() for r in related]))
    if comparisons:
        graph[concept_lower]["comparisons"] = list(set(graph[concept_lower]["comparisons"] + [c.lower() for c in comparisons]))

    save_concept_graph(graph)
    return graph[concept_lower]


def generate_concept_relationships(topic):
    """
    Use AI to extract concept relationships for a topic.
    Returns dict with parents, children, related, comparisons.
    """
    prompt = f"""Analyze the concept "{topic}" and identify its relationships.

Return ONLY a JSON object with these keys (no other text):
{{
    "parents": ["broader concepts this falls under, max 3"],
    "children": ["narrower sub-concepts, max 5"],
    "related": ["related but not hierarchical concepts, max 5"],
    "comparisons": ["concepts commonly compared with this, max 3"]
}}

Rules:
- Use lowercase for all terms
- Only include real, commonly searched concepts
- Parents should be broader categories
- Children should be specific subtopics
- Related should be adjacent concepts
- Comparisons should be things people often confuse or compare

Example for "compound interest":
{{
    "parents": ["interest", "finance"],
    "children": ["compound interest formula", "continuous compounding", "compound frequency"],
    "related": ["time value of money", "exponential growth", "savings account"],
    "comparisons": ["simple interest"]
}}

Now analyze: "{topic}"
"""

    try:
        # Use same provider priority as main generation (Groq first)
        if GROQ_API_KEY and OPENAI_SDK_AVAILABLE:
            response = generate_with_groq(prompt)
        elif GENAI_AVAILABLE and GOOGLE_API_KEY:
            response = generate_with_gemini_prompt(prompt)
        else:
            response = generate_with_requests_prompt(prompt)

        # Extract JSON from response
        # Handle potential markdown code blocks
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)

    except Exception as e:
        log(f"Failed to generate relationships for {topic}: {e}", "ERROR")
        return {"parents": [], "children": [], "related": [], "comparisons": []}


def build_concept_graph_for_topics(topics=None, use_ai=True):
    """
    Build/expand the concept graph for given topics.

    Args:
        topics: List of topics, or None for all TOPIC_CATEGORIES
        use_ai: Whether to use AI to generate relationships
    """
    if topics is None:
        topics = []
        for category, topic_list in TOPIC_CATEGORIES.items():
            if category not in ["comparisons", "classifications"]:
                topics.extend(topic_list)

    graph = load_concept_graph()
    added = 0

    for topic in topics:
        topic_lower = topic.lower()

        # Skip if already in graph with relationships
        if topic_lower in graph and any(graph[topic_lower].values()):
            continue

        log(f"Building graph for: {topic}")

        if use_ai:
            relationships = generate_concept_relationships(topic)
            add_concept_to_graph(
                topic,
                parents=relationships.get("parents", []),
                children=relationships.get("children", []),
                related=relationships.get("related", []),
                comparisons=relationships.get("comparisons", []),
            )
            added += 1

            # Rate limiting
            import time
            time.sleep(1)
        else:
            # Just add empty entry
            add_concept_to_graph(topic)
            added += 1

    log(f"Added {added} concepts to graph", "SUCCESS")
    return load_concept_graph()


def get_comparison_pairs_from_graph():
    """
    Extract all comparison pairs from the concept graph.
    Returns list of "X vs Y" strings for comparison page generation.
    """
    graph = load_concept_graph()
    pairs = set()

    for concept, relations in graph.items():
        for comparison in relations.get("comparisons", []):
            # Create canonical pair (alphabetical order to avoid duplicates)
            pair = tuple(sorted([concept, comparison]))
            pairs.add(pair)

    # Format as "X vs Y"
    return [f"{a} vs {b}" for a, b in pairs]


def get_child_topics_from_graph():
    """
    Extract all child topics from the graph for expansion.
    Returns list of topics that could be generated.
    """
    graph = load_concept_graph()
    children = set()

    for concept, relations in graph.items():
        for child in relations.get("children", []):
            children.add(child)

    return list(children)


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
# COMPLETENESS TRACKING (Upgrade 4: Done Metrics)
# =============================================================================
# Four metrics define "DONE":
# 1. Concept Coverage: Do we have pages for all concepts?
# 2. Angle Coverage: Does each concept have all 12 angles?
# 3. Graph Connectivity: Are concepts connected (no orphans)?
# 4. Question Coverage: Do all question frames resolve to pages?

def calculate_concept_coverage(category=None):
    """
    METRIC 1: Concept Coverage
    What % of canonical concepts have at least one page?

    Returns: dict with count, total, percentage
    """
    log_data = load_generated_log()
    generated = set(g.lower() for g in log_data.get("generated", []))

    # Get all base concepts (not expansions)
    if category:
        concepts = [t.lower() for t in TOPIC_CATEGORIES.get(category, [])]
    else:
        concepts = []
        for cat, topics in TOPIC_CATEGORIES.items():
            if cat not in ["comparisons", "classifications"]:
                concepts.extend(t.lower() for t in topics)

    # Check which concepts have at least one page (base or any angle)
    covered = 0
    uncovered = []

    for concept in concepts:
        # Check if base concept or any angle exists
        has_page = concept in generated
        if not has_page:
            for pattern in CANONICAL_EXPANSIONS:
                expanded = pattern.format(topic=concept).lower()
                if expanded in generated:
                    has_page = True
                    break

        if has_page:
            covered += 1
        else:
            uncovered.append(concept)

    total = len(concepts)
    percentage = (covered / total * 100) if total > 0 else 0

    return {
        "covered": covered,
        "total": total,
        "percentage": percentage,
        "uncovered": uncovered[:20],  # First 20 uncovered
        "done": percentage >= 98.0,
    }


def calculate_angle_coverage(category=None):
    """
    METRIC 2: Angle Coverage
    What % of concepts have all 12 canonical angles?

    Returns: dict with stats and gaps
    """
    log_data = load_generated_log()
    generated = set(g.lower() for g in log_data.get("generated", []))

    # Get base concepts
    if category:
        concepts = [t.lower() for t in TOPIC_CATEGORIES.get(category, [])]
    else:
        concepts = []
        for cat, topics in TOPIC_CATEGORIES.items():
            if cat not in ["comparisons", "classifications"]:
                concepts.extend(t.lower() for t in topics)

    # Required angles (excluding optional structure angles)
    required_angles = [a for a in CANONICAL_ANGLES if a not in OPTIONAL_ANGLES]
    num_required = len(required_angles)  # 9 required angles

    # Track coverage per concept
    fully_covered = 0
    partial_coverage = []
    gaps = []

    for concept in concepts:
        angles_present = 0
        missing_angles = []

        for pattern in CANONICAL_EXPANSIONS:
            expanded = pattern.format(topic=concept).lower()
            angle_type = EXPANSION_TO_PROMPT_TYPE.get(pattern, "definition")

            if expanded in generated:
                angles_present += 1
            elif angle_type not in OPTIONAL_ANGLES:
                missing_angles.append(angle_type)

        # Count as fully covered if >= 10/12 angles (allowing 2 optional missing)
        if angles_present >= 10:
            fully_covered += 1
        else:
            partial_coverage.append({
                "concept": concept,
                "angles": angles_present,
                "missing": missing_angles[:3],
            })

    total = len(concepts)
    percentage = (fully_covered / total * 100) if total > 0 else 0

    # Get top gaps (most common missing angles)
    angle_gaps = {}
    for pc in partial_coverage:
        for angle in pc.get("missing", []):
            angle_gaps[angle] = angle_gaps.get(angle, 0) + 1

    top_gaps = sorted(angle_gaps.items(), key=lambda x: -x[1])[:5]

    return {
        "fully_covered": fully_covered,
        "total": total,
        "percentage": percentage,
        "partial": partial_coverage[:10],
        "top_gaps": top_gaps,
        "done": percentage >= 95.0,
    }


def calculate_graph_connectivity():
    """
    METRIC 3: Graph Connectivity
    What % of concepts are orphans (no connections)?

    Returns: dict with orphan stats
    """
    graph = load_concept_graph()

    if not graph:
        return {
            "total_nodes": 0,
            "orphans": 0,
            "orphan_percentage": 100.0,
            "orphan_list": [],
            "done": False,
        }

    orphans = []

    for concept, relations in graph.items():
        has_parent = bool(relations.get("parents"))
        has_child = bool(relations.get("children"))
        has_related = bool(relations.get("related"))
        has_comparison = bool(relations.get("comparisons"))

        # Orphan if no connections at all
        if not (has_parent or has_child or has_related or has_comparison):
            orphans.append(concept)

    total = len(graph)
    orphan_count = len(orphans)
    orphan_percentage = (orphan_count / total * 100) if total > 0 else 100

    return {
        "total_nodes": total,
        "orphans": orphan_count,
        "orphan_percentage": orphan_percentage,
        "orphan_list": orphans[:20],
        "done": orphan_percentage <= 2.0,
    }


def calculate_question_coverage(category=None):
    """
    METRIC 4: Question-Space Coverage
    What % of (concept x question_frame) combinations resolve to pages?

    Returns: dict with coverage stats
    """
    log_data = load_generated_log()
    generated = set(g.lower() for g in log_data.get("generated", []))

    # Get base concepts
    if category:
        concepts = [t.lower() for t in TOPIC_CATEGORIES.get(category, [])]
    else:
        concepts = []
        for cat, topics in TOPIC_CATEGORIES.items():
            if cat not in ["comparisons", "classifications"]:
                concepts.extend(t.lower() for t in topics)

    # Count all question-frame combinations
    total_questions = 0
    resolved_questions = 0
    unresolved = []

    for concept in concepts:
        for pattern in CANONICAL_EXPANSIONS:
            question = pattern.format(topic=concept).lower()
            total_questions += 1

            if question in generated:
                resolved_questions += 1
            else:
                if len(unresolved) < 50:
                    unresolved.append(question)

    percentage = (resolved_questions / total_questions * 100) if total_questions > 0 else 0

    return {
        "resolved": resolved_questions,
        "total": total_questions,
        "percentage": percentage,
        "unresolved": unresolved[:20],
        "done": percentage >= 95.0,
    }


def calculate_completeness(category=None):
    """
    Calculate all five completeness metrics.

    Returns: dict with all metrics and overall done status
    """
    concept_cov = calculate_concept_coverage(category)
    angle_cov = calculate_angle_coverage(category)
    graph_conn = calculate_graph_connectivity()
    question_cov = calculate_question_coverage(category)
    calc_cov = calculate_calculator_coverage(category)

    # Overall done: all 5 metrics pass
    all_done = (
        concept_cov["done"] and
        angle_cov["done"] and
        graph_conn["done"] and
        question_cov["done"] and
        calc_cov["done"]
    )

    return {
        "concept_coverage": concept_cov,
        "angle_coverage": angle_cov,
        "graph_connectivity": graph_conn,
        "question_coverage": question_cov,
        "calculator_coverage": calc_cov,
        "all_done": all_done,
        "category": category or "all",
    }


def calculate_calculator_coverage(category=None):
    """
    METRIC 5: Calculator Coverage
    What % of calculator-eligible pages have working calculators?

    Returns: dict with calculator stats
    """
    if not CALCULATORS_AVAILABLE:
        return {
            "eligible": 0,
            "covered": 0,
            "percentage": 0,
            "missing": [],
            "done": True,  # No calculators module = skip this metric
        }

    from calculators import CALCULATOR_TOPICS, CALCULATORS

    # Get base concepts for category
    if category:
        concepts = [t.lower() for t in TOPIC_CATEGORIES.get(category, [])]
    else:
        concepts = []
        for cat, topics in TOPIC_CATEGORIES.items():
            if cat not in ["comparisons", "classifications"]:
                concepts.extend(t.lower() for t in topics)

    eligible = []
    covered = []
    missing = []

    for concept in concepts:
        calc_type = CALCULATOR_TOPICS.get(concept)

        if calc_type is None:
            # Explicitly marked as no calculator needed
            continue

        eligible.append(concept)

        if calc_type in CALCULATORS:
            covered.append(concept)
        else:
            missing.append({"concept": concept, "calc_type": calc_type})

    total_eligible = len(eligible)
    total_covered = len(covered)
    percentage = (total_covered / total_eligible * 100) if total_eligible > 0 else 100

    return {
        "eligible": total_eligible,
        "covered": total_covered,
        "percentage": percentage,
        "missing": missing[:20],
        "done": percentage >= 95.0,
    }


def get_next_actions(completeness):
    """
    Based on completeness metrics, recommend what to do next.

    Returns: list of actionable recommendations
    """
    actions = []

    cc = completeness["concept_coverage"]
    ac = completeness["angle_coverage"]
    gc = completeness["graph_connectivity"]
    qc = completeness["question_coverage"]

    # Priority 1: Concept coverage (need base concepts first)
    if not cc["done"]:
        uncovered = cc.get("uncovered", [])[:5]
        actions.append({
            "priority": 1,
            "action": "Generate base definition pages",
            "reason": f"Only {cc['percentage']:.1f}% concept coverage (need 98%)",
            "command": f"--topic \"{uncovered[0]}\"" if uncovered else "--count 10",
            "targets": uncovered,
        })

    # Priority 2: Graph connectivity (need relationships)
    if not gc["done"] and gc["total_nodes"] < len(TOPIC_CATEGORIES.get("finance", [])):
        actions.append({
            "priority": 2,
            "action": "Build concept graph",
            "reason": f"Only {gc['total_nodes']} concepts in graph",
            "command": "--build-graph --count 20",
        })

    # Priority 3: Angle coverage (expand existing concepts)
    if not ac["done"] and cc["percentage"] > 50:
        top_gaps = ac.get("top_gaps", [])
        gap_angles = [g[0] for g in top_gaps[:3]]
        actions.append({
            "priority": 3,
            "action": "Generate missing angles",
            "reason": f"Only {ac['percentage']:.1f}% angle coverage (need 95%)",
            "command": "--generate-expanded --count 20",
            "focus_angles": gap_angles,
        })

    # Priority 4: Question coverage
    if not qc["done"] and ac["percentage"] > 80:
        actions.append({
            "priority": 4,
            "action": "Fill question gaps",
            "reason": f"Only {qc['percentage']:.1f}% question coverage (need 95%)",
            "command": "--generate-expanded --count 50",
        })

    if not actions:
        actions.append({
            "priority": 0,
            "action": "Domain complete!",
            "reason": "All metrics pass thresholds",
            "command": "Move to next domain",
        })

    return sorted(actions, key=lambda x: x["priority"])


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


def generate_with_grok(prompt, model="grok-2"):
    """
    Generate content using xAI Grok API.
    Uses OpenAI-compatible SDK with xAI base URL.

    Models available:
    - grok-2: Most capable ($5/$15 per 1M tokens)
    - grok-2-mini: Faster, cheaper ($2/$10 per 1M tokens)
    """
    if not OPENAI_SDK_AVAILABLE:
        raise Exception("OpenAI SDK not installed. Run: pip install openai")

    if not XAI_API_KEY:
        raise Exception("XAI_API_KEY not configured in config.py")

    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert educational content writer creating evergreen reference pages."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def generate_with_groq(prompt, model="llama-3.3-70b-versatile"):
    """
    Generate content using Groq API (fast inference).
    Uses OpenAI-compatible SDK with Groq base URL.

    Models available:
    - llama-3.3-70b-versatile: Best quality (recommended)
    - llama-3.1-8b-instant: Faster, smaller
    - mixtral-8x7b-32768: Good alternative
    - gemma2-9b-it: Google's Gemma

    Free tier: 30 requests/minute, 14,400 requests/day
    """
    if not OPENAI_SDK_AVAILABLE:
        raise Exception("OpenAI SDK not installed. Run: pip install openai")

    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not configured in config.py")

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert educational content writer creating evergreen reference pages."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def detect_page_type(topic):
    """
    Detect what type of page this topic needs.

    Returns one of the 12 canonical angles + comparison/classification:
    - "definition" (default - what is X)
    - "comparison" (X vs Y)
    - "classification" (for items in classifications category)
    - "how" (how does X work)
    - "why" (why X matters)
    - "examples" (examples of X)
    - "parts" (parts of X)
    - "stages" (stages of X)
    - "types" (types of X)
    - "affects" (what affects X)
    - "depends" (what X depends on)
    - "used_for" (what X is used for)
    - "misconceptions" (common misconceptions about X)
    - "beginner" (X for beginners)
    """
    topic_lower = topic.lower()

    # Comparison pages (X vs Y)
    if " vs " in topic_lower or " versus " in topic_lower:
        return "comparison"

    # Structure angles (parts/stages/types) - check before generic classification
    if topic_lower.startswith("parts of "):
        return "parts"
    if topic_lower.startswith("stages of "):
        return "stages"
    if topic_lower.startswith("types of ") or topic_lower.startswith("kinds of "):
        return "types"

    # Other classification patterns (layers, levels, branches, forms)
    classification_keywords = ["layers of", "levels of", "branches of", "forms of"]
    for keyword in classification_keywords:
        if topic_lower.startswith(keyword):
            return "classification"

    # Question-frame pages
    if topic_lower.startswith("how does ") and " work" in topic_lower:
        return "how"
    if topic_lower.startswith("how ") and " works" in topic_lower:
        return "how"
    if topic_lower.startswith("why ") and " matters" in topic_lower:
        return "why"
    if topic_lower.startswith("why ") and " is important" in topic_lower:
        return "why"
    if topic_lower.startswith("examples of "):
        return "examples"

    # Relationship angles
    if topic_lower.startswith("what affects "):
        return "affects"
    if topic_lower.startswith("what ") and " depends on" in topic_lower:
        return "depends"
    if topic_lower.startswith("what ") and " is used for" in topic_lower:
        return "used_for"

    # Clarification angles
    if topic_lower.startswith("common misconceptions about "):
        return "misconceptions"
    if topic_lower.startswith("myths about "):
        return "misconceptions"
    if topic_lower.endswith(" for beginners"):
        return "beginner"
    if topic_lower.startswith("introduction to "):
        return "beginner"
    if topic_lower.startswith("beginner's guide to "):
        return "beginner"

    # Default: definition page
    return "definition"


def get_prompt_for_topic(topic):
    """Get the appropriate prompt template for a topic."""
    page_type = detect_page_type(topic)

    # Extract base topic for question-frame prompts
    base_topic = extract_base_topic(topic)

    if page_type == "comparison":
        return COMPARISON_PAGE_PROMPT.format(topic=topic)
    elif page_type == "classification":
        return CLASSIFICATION_PAGE_PROMPT.format(topic=topic)
    elif page_type == "how":
        return HOW_IT_WORKS_PROMPT.format(topic=base_topic)
    elif page_type == "why":
        return WHY_IT_MATTERS_PROMPT.format(topic=base_topic)
    elif page_type == "examples":
        return EXAMPLES_PROMPT.format(topic=base_topic)
    elif page_type in ("parts", "stages", "types"):
        # Structure angles use classification prompt
        return CLASSIFICATION_PAGE_PROMPT.format(topic=topic)
    elif page_type == "affects":
        return WHAT_AFFECTS_PROMPT.format(topic=base_topic)
    elif page_type == "depends":
        return WHAT_DEPENDS_ON_PROMPT.format(topic=base_topic)
    elif page_type == "used_for":
        return WHAT_USED_FOR_PROMPT.format(topic=base_topic)
    elif page_type == "misconceptions":
        return MISCONCEPTIONS_PROMPT.format(topic=base_topic)
    elif page_type == "beginner":
        return BEGINNER_GUIDE_PROMPT.format(topic=base_topic)
    else:
        return KNOWLEDGE_PAGE_PROMPT.format(topic=topic)


def extract_base_topic(topic):
    """
    Extract the base topic from a question-framed topic.

    Examples:
    - "how does compound interest work" -> "compound interest"
    - "examples of photosynthesis" -> "photosynthesis"
    - "compound interest for beginners" -> "compound interest"
    - "parts of a cell" -> "a cell"
    - "what affects inflation" -> "inflation"
    - "what gravity is used for" -> "gravity"
    """
    topic_lower = topic.lower()

    # Remove question frames (order matters - longer patterns first)
    prefixes = [
        "common misconceptions about ",
        "beginner's guide to ",
        "introduction to ",
        "how does ",
        "examples of ",
        "myths about ",
        "parts of ",
        "stages of ",
        "types of ",
        "kinds of ",
        "what affects ",
        "how ",
        "why ",
        "what ",
    ]

    suffixes = [
        " is used for",
        " depends on",
        " for beginners",
        " is important",
        " matters",
        " works",
        " work",
    ]

    result = topic_lower

    for prefix in prefixes:
        if result.startswith(prefix):
            result = result[len(prefix):]
            break

    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[:-len(suffix)]
            break

    return result.strip()


def generate_content(topic, provider=None):
    """
    Generate page content using available method.

    Provider priority (if not specified):
    1. Groq - if GROQ_API_KEY is set (fast, free tier)
    2. Grok (xAI) - if XAI_API_KEY is set
    3. Gemini - if GOOGLE_API_KEY is set
    """
    try:
        prompt = get_prompt_for_topic(topic)
        page_type = detect_page_type(topic)
        log(f"  Page type: {page_type}")

        # Determine provider
        if provider is None:
            if GROQ_API_KEY and OPENAI_SDK_AVAILABLE:
                provider = "groq"
            elif XAI_API_KEY and OPENAI_SDK_AVAILABLE:
                provider = "grok"
            elif GENAI_AVAILABLE and GOOGLE_API_KEY:
                provider = "gemini"
            elif GOOGLE_API_KEY:
                provider = "gemini-rest"
            else:
                raise Exception("No API key configured (GROQ_API_KEY, XAI_API_KEY, or GOOGLE_API_KEY)")

        log(f"  Provider: {provider}")

        if provider == "groq":
            return generate_with_groq(prompt)
        elif provider == "grok":
            return generate_with_grok(prompt, model="grok-2")
        elif provider == "gemini":
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


def format_as_markdown(topic, content, page_title=None):
    """Format content as Markdown."""
    slug = slugify(topic)

    # Use provided title or fall back to topic-based title
    if page_title is None:
        page_title = f"What is {topic.title()}?"

    md = f"""---
title: "{page_title}"
slug: {slug}
description: "A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions."
date: {datetime.now().strftime("%Y-%m-%d")}
---

# {page_title}

{content}

---

*This is an evergreen reference page. Content is factual and timeless.*
"""
    return md


def get_page_title(topic):
    """Generate appropriate title based on page type."""
    page_type = detect_page_type(topic)
    base_topic = extract_base_topic(topic)

    if page_type == "comparison":
        # "ETF vs Mutual Fund" -> "ETF vs Mutual Fund: Key Differences Explained"
        return f"{topic.title()}: Key Differences Explained"
    elif page_type == "classification":
        # "Types of Ecosystems" -> "Types of Ecosystems: Complete Guide"
        return f"{topic.title()}: Complete Guide"
    elif page_type == "how":
        # "how does compound interest work" -> "How Does Compound Interest Work?"
        return f"How Does {base_topic.title()} Work?"
    elif page_type == "why":
        # "why compound interest matters" -> "Why Compound Interest Matters"
        return f"Why {base_topic.title()} Matters"
    elif page_type == "examples":
        # "examples of photosynthesis" -> "Examples of Photosynthesis"
        return f"Examples of {base_topic.title()}"
    elif page_type == "misconceptions":
        # "common misconceptions about X" -> "Common Misconceptions About X"
        return f"Common Misconceptions About {base_topic.title()}"
    elif page_type == "beginner":
        # "X for beginners" -> "X for Beginners: A Simple Guide"
        return f"{base_topic.title()} for Beginners: A Simple Guide"
    else:
        # "Compound Interest" -> "What is Compound Interest?"
        return f"What is {topic.title()}?"


def generate_toc_html(content):
    """Generate a table of contents from h2 headings in raw content.
    Extracts headings from ## markdown and [SECTION] tags.
    Returns empty string if fewer than 2 headings found."""
    import re
    headings = []
    for line in content.strip().split('\n'):
        stripped = line.strip()
        # Markdown h2
        if stripped.startswith('## '):
            heading_text = stripped[3:].strip()
            headings.append(heading_text)
        # [SECTION] tag
        section_match = re.match(r'^\[SECTION\]\s*(.+?)\s*\[/SECTION\]$', stripped)
        if section_match:
            headings.append(section_match.group(1))

    if len(headings) < 2:
        return ""

    items = ""
    for h in headings:
        slug = slugify(h)
        # Strip bold markers for display
        display = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
        items += f'        <li><a href="#{slug}">{display}</a></li>\n'

    return f"""<nav class="toc">
    <h3>In This Article</h3>
    <ol>
{items}    </ol>
</nav>"""


def generate_angle_crossref_html(concept_slug, angle_id, domain_slug):
    """Generate a 'See Also' box with links to related angles for the same concept."""
    # Map each angle to its most relevant siblings
    angle_relations = {
        "what-is": ["how-it-works", "types-of", "example-of"],
        "how-it-works": ["what-is", "what-affects-it", "example-of"],
        "types-of": ["what-is", "example-of", "common-misconceptions-about"],
        "example-of": ["what-is", "types-of", "how-it-works"],
        "common-misconceptions-about": ["what-is", "how-it-works", "example-of"],
        "what-affects-it": ["how-it-works", "what-it-depends-on", "what-is"],
        "what-it-depends-on": ["what-affects-it", "how-it-works", "what-is"],
        "vs": ["what-is", "types-of", "how-it-works"],
    }

    from templates import ANGLE_DISPLAY, angle_url

    related_angles = angle_relations.get(angle_id, [])
    if not related_angles:
        return ""

    # Check which angle files actually exist
    existing = []
    for ra in related_angles:
        angle_file = OUTPUT_DIR / f"{domain_slug}_structured" / concept_slug / f"{ra}.json"
        if angle_file.exists():
            display = ANGLE_DISPLAY.get(ra, ra.replace("-", " ").title())
            href = angle_url(domain_slug, concept_slug, ra)
            existing.append((display, href))

    if not existing:
        return ""

    items = ""
    for display, href in existing:
        items += f'            <li><a href="{href}">{display}</a></li>\n'

    concept_display = concept_slug.replace("-", " ").title()
    return f"""<div class="see-also">
    <h3>See Also: {concept_display}</h3>
    <ul>
{items}    </ul>
</div>"""


def markdown_to_html(content):
    """Convert markdown/tag content to HTML.
    Handles both markdown (##, *, |) and structured tags
    ([FACTBOX], [CALLOUT], [SECTION], [TABLE], [RATING])."""
    import re

    def bold(text):
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    lines = content.strip().split('\n')
    html_lines = []
    in_list = False
    in_ol = False
    in_table = False
    in_factbox = False
    in_callout = False
    table_header_done = False

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

        # Skip empty lines (close open lists but not other blocks)
        if not stripped:
            if not in_table and not in_factbox and not in_callout:
                close_list()
            continue

        # ── [FACTBOX] / [/FACTBOX] ──
        if stripped == '[FACTBOX]':
            close_list()
            in_factbox = True
            html_lines.append('<div class="factbox"><h3>Quick Facts</h3>')
            continue
        if stripped == '[/FACTBOX]':
            in_factbox = False
            html_lines.append('</div>')
            continue
        if in_factbox:
            if ':' in stripped:
                key, _, val = stripped.partition(':')
                html_lines.append(f'<div class="fact-row"><span class="fact-key">{bold(key.strip())}</span><span class="fact-val">{bold(val.strip())}</span></div>')
            continue

        # ── [CALLOUT] / [/CALLOUT] ──
        if stripped == '[CALLOUT]':
            close_list()
            in_callout = True
            html_lines.append('<div class="callout">')
            continue
        if stripped == '[/CALLOUT]':
            in_callout = False
            html_lines.append('</div>')
            continue
        # Inline callout: [CALLOUT] text [/CALLOUT]
        callout_inline = re.match(r'^\[CALLOUT\]\s*(.+?)\s*\[/CALLOUT\]$', stripped)
        if callout_inline:
            close_list()
            html_lines.append(f'<div class="callout"><p>{bold(callout_inline.group(1))}</p></div>')
            continue
        if in_callout:
            if stripped.startswith('Misconception:') or stripped.startswith('Reality:'):
                key, _, val = stripped.partition(':')
                css_class = 'misconception' if key.strip() == 'Misconception' else 'reality'
                html_lines.append(f'<p class="{css_class}"><strong>{key.strip()}:</strong> {bold(val.strip())}</p>')
            else:
                html_lines.append(f'<p>{bold(stripped)}</p>')
            continue

        # ── [SECTION] Name [/SECTION] ──
        section_match = re.match(r'^\[SECTION\]\s*(.+?)\s*\[/SECTION\]$', stripped)
        if section_match:
            close_list()
            html_lines.append(f'<h2 id="{slugify(section_match.group(1))}">{bold(section_match.group(1))}</h2>')
            continue

        # ── [TABLE] / [/TABLE] ──
        if stripped == '[TABLE]':
            close_list()
            in_table = True
            table_header_done = False
            html_lines.append('<div class="table-wrapper"><table>')
            continue
        if stripped == '[/TABLE]':
            if table_header_done:
                html_lines.append('</tbody>')
            html_lines.append('</table></div>')
            in_table = False
            table_header_done = False
            continue

        # ── [RATING] label: X/5 ──
        rating_match = re.match(r'^\[RATING\]\s*(.+?):\s*(\d)/5', stripped)
        if rating_match:
            close_list()
            label = rating_match.group(1)
            score = int(rating_match.group(2))
            filled = '●' * score + '○' * (5 - score)
            html_lines.append(f'<div class="rating"><span class="rating-label">{bold(label)}</span><span class="rating-dots">{filled}</span><span class="rating-score">{score}/5</span></div>')
            continue

        # ── Table rows (pipe-delimited, inside [TABLE] or bare) ──
        if stripped.startswith('|') and stripped.endswith('|'):
            if re.match(r'^[\|\s\-:]+$', stripped):
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if not in_table:
                close_list()
                in_table = True
                table_header_done = False
                html_lines.append('<div class="table-wrapper"><table>')
            if not table_header_done:
                html_lines.append('<thead><tr>' + ''.join(f'<th>{bold(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                table_header_done = True
            else:
                html_lines.append('<tr>' + ''.join(f'<td>{bold(c)}</td>' for c in cells) + '</tr>')
            continue

        # Close bare table if non-table line
        if in_table and not stripped.startswith('|'):
            if table_header_done:
                html_lines.append('</tbody>')
            html_lines.append('</table></div>')
            in_table = False
            table_header_done = False

        # ── Markdown headers ──
        if stripped.startswith('## '):
            close_list()
            html_lines.append(f'<h2 id="{slugify(stripped[3:])}">{bold(stripped[3:])}</h2>')
            continue
        if stripped.startswith('### '):
            close_list()
            html_lines.append(f'<h3>{bold(stripped[4:])}</h3>')
            continue

        # ── Bold subheader: **Label:** (standalone) ──
        bold_header = re.match(r'^\*\*(.+?)\*\*:?\s*$', stripped)
        if bold_header:
            close_list()
            html_lines.append(f'<h3>{bold_header.group(1)}</h3>')
            continue

        # ── Bold label with inline content: **Label:** text ──
        bold_inline = re.match(r'^\*\*(.+?)\*\*:\s+(.+)', stripped)
        if bold_inline:
            close_list()
            html_lines.append(f'<p><strong>{bold_inline.group(1)}:</strong> {bold(bold_inline.group(2))}</p>')
            continue

        # ── Bullet points ──
        if re.match(r'^[-*•]\s+', stripped):
            if not in_list:
                close_list()
                html_lines.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*•]\s+', '', stripped)
            html_lines.append(f'<li>{bold(item)}</li>')
            continue

        # ── Numbered list ──
        ol_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if ol_match:
            if not in_ol:
                close_list()
                html_lines.append('<ol>')
                in_ol = True
            html_lines.append(f'<li>{bold(ol_match.group(2))}</li>')
            continue

        # ── Close list for non-list content ──
        close_list()

        # ── Indented continuation (skip) ──
        if line.startswith('  ') and not stripped.startswith('<'):
            continue

        # ── Regular paragraph ──
        html_lines.append(f'<p>{bold(stripped)}</p>')

    # Close any open tags
    close_list()
    if in_table:
        if table_header_done:
            html_lines.append('</tbody>')
        html_lines.append('</table></div>')
    if in_factbox:
        html_lines.append('</div>')
    if in_callout:
        html_lines.append('</div>')

    return '\n'.join(html_lines)


def format_as_html(topic, content, page_title=None, domain_slug=None,
                   concept_slug=None, angle_id=None, all_angles=None,
                   canonical_path=None, all_concepts=None):
    """Format content as standalone HTML with embedded calculator if applicable."""
    from templates import (
        SHARED_CSS, ARTICLE_CSS, RELATED_CSS, DOMAIN_META,
        generate_header_html, generate_footer_html,
        generate_breadcrumb_html, generate_sidebar_html,
        generate_article_jsonld, generate_og_tags,
        generate_related_concepts_html,
    )

    slug = slugify(topic)
    # Use provided title or fall back to auto-detected title
    if page_title is None:
        page_title = get_page_title(topic)
    page_type = detect_page_type(topic)

    # Convert markdown content to HTML
    html_content = markdown_to_html(content)

    # Generate TOC
    toc_html = generate_toc_html(content)

    # Get calculator if applicable
    calculator_html = get_calculator_html(topic) or ""
    if calculator_html:
        log(f"  Adding calculator for: {topic}", "SUCCESS")
        # Wrap calculator in callout box if present
        calculator_html = f'<div class="calculator-callout"><div class="calculator-callout-header">Calculator</div><div class="calculator-callout-body">{calculator_html}</div></div>'

    # Generate meta description based on page type
    base_topic = extract_base_topic(topic)

    if page_type == "comparison":
        meta_desc = f"Compare {topic} - key differences, similarities, and when to use each. Clear explanation with examples."
    elif page_type == "classification":
        meta_desc = f"Complete guide to {topic} - all categories explained with definitions and examples."
    elif page_type == "how":
        meta_desc = f"Learn how {base_topic} works with this step-by-step explanation. Simple guide to the process and mechanism."
    elif page_type == "why":
        meta_desc = f"Understand why {base_topic} matters - real-world impact, importance, and relevance explained simply."
    elif page_type == "examples":
        meta_desc = f"Clear examples of {base_topic} from everyday life. Concrete illustrations to help you understand the concept."
    elif page_type == "misconceptions":
        meta_desc = f"Common misconceptions about {base_topic} debunked. Learn what people get wrong and the real facts."
    elif page_type == "beginner":
        meta_desc = f"{base_topic.title()} explained for beginners. Simple introduction with key terms and first steps."
    else:
        meta_desc = f"A clear, simple explanation of {topic} - definition, key concepts, examples, and common misconceptions."

    # Build canonical path
    if canonical_path is None and domain_slug and concept_slug and angle_id:
        canonical_path = f"{domain_slug}/{concept_slug}/{angle_id}.html"

    # Build layout components
    header_html = generate_header_html(active_domain=domain_slug)
    footer_html = generate_footer_html()

    breadcrumb_html = ""
    sidebar_html = ""
    jsonld_html = ""
    og_html = ""
    related_html = ""
    if domain_slug and concept_slug and angle_id:
        breadcrumb_html = generate_breadcrumb_html(domain_slug, concept_slug, angle_id)
        jsonld_html = generate_article_jsonld(page_title, meta_desc, canonical_path or "", domain_slug, concept_slug, angle_id)
    if domain_slug and concept_slug and angle_id and all_angles:
        sidebar_html = generate_sidebar_html(domain_slug, concept_slug, angle_id, all_angles)
    if canonical_path:
        og_html = generate_og_tags(page_title, meta_desc, canonical_path)
    crossref_html = ""
    if domain_slug and concept_slug and angle_id:
        crossref_html = generate_angle_crossref_html(concept_slug, angle_id, domain_slug)

    # Load concept categories for semantic related linking
    concept_categories = None
    if domain_slug:
        canonical_data = load_canonical_concepts(domain_slug)
        if canonical_data:
            concept_categories = canonical_data.get("concepts", {})
    if domain_slug and concept_slug and all_concepts:
        related_html = generate_related_concepts_html(domain_slug, concept_slug, all_concepts, concept_categories=concept_categories)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://360library.com/{canonical_path}">
    {og_html}
    <title>{page_title} - 360Library</title>
    <style>
{SHARED_CSS}
{ARTICLE_CSS}
{RELATED_CSS}
    </style>
    {jsonld_html}
</head>
<body>
{header_html}

{breadcrumb_html}

<div class="article-wrapper" style="--domain-color: {DOMAIN_META.get(domain_slug, {}).get('color', '#1B4D8E')}">
    <main class="article-main">
        <article>
            <h1>{page_title}</h1>
            <div class="article-meta">Last updated: {datetime.now().strftime("%B %Y")}</div>

            {toc_html}

            {calculator_html}

            {html_content}

            {crossref_html}

            {related_html}
        </article>
    </main>

    {sidebar_html}
</div>

{footer_html}
</body>
</html>
"""
    return html


def format_as_json(topic, content, category="general", angle_id="what-is", base_concept=None):
    """Format as structured JSON for API/licensing."""
    slug = slugify(topic)
    concept = base_concept or topic

    # Use angle-aware title
    title = get_angle_title(concept, angle_id)

    data = {
        "slug": slug,
        "topic": topic,
        "base_concept": concept,
        "angle": angle_id,
        "title": title,
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

def generate_knowledge_page(topic, category="general", output_formats=None, angle_id="what-is", base_concept=None):
    """
    Generate a complete knowledge page for a topic.

    Args:
        topic: The topic to explain (can be full phrase like "what affects compound interest")
        category: Topic category for organization
        output_formats: List of formats to output (markdown, html, json)
        angle_id: The canonical angle ID (what-is, how-it-works, etc.)
        base_concept: The base concept name (e.g., "compound interest")

    Returns:
        Dict with paths to generated files
    """
    if output_formats is None:
        output_formats = ["markdown", "html", "json"]

    # Use topic as base_concept if not provided
    if base_concept is None:
        base_concept = topic

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

    # Get the correct title for this angle
    page_title = get_angle_title(base_concept, angle_id)

    if "markdown" in output_formats:
        md_content = format_as_markdown(topic, content, page_title=page_title)
        md_path = category_dir / f"{slug}.md"
        md_path.write_text(md_content, encoding="utf-8")
        results["files"]["markdown"] = str(md_path)
        log(f"  Saved: {md_path.name}")

    if "html" in output_formats:
        # Determine all sibling angles for the sidebar
        concept_dir = category_dir
        sibling_angles = []
        if concept_dir.exists():
            sibling_angles = [f.stem for f in concept_dir.glob("*.html") if f.stem != slug]
        if angle_id and angle_id not in sibling_angles:
            sibling_angles.append(angle_id)
        # Derive domain_slug and concept_slug from category path
        domain_slug = category.split("/")[0] if "/" in category else category
        concept_slug_for_template = category.split("/")[1] if "/" in category else (base_concept.replace(" ", "-").lower() if base_concept else slug)
        html_content = format_as_html(
            topic, content, page_title=page_title,
            domain_slug=domain_slug,
            concept_slug=concept_slug_for_template,
            angle_id=angle_id,
            all_angles=sibling_angles,
        )
        html_path = category_dir / f"{slug}.html"
        html_path.write_text(html_content, encoding="utf-8")
        results["files"]["html"] = str(html_path)
        log(f"  Saved: {html_path.name}")

    if "json" in output_formats:
        json_content = format_as_json(topic, content, category, angle_id=angle_id, base_concept=base_concept)
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
# REBUILD PIPELINE
# =============================================================================

def rebuild_all_html():
    """Re-render all HTML pages from stored JSON data.
    Applies new template features (TOC, cross-refs, meta, calculator callout)
    without regenerating content from AI.
    """
    from templates import DOMAIN_META

    json_files = list(OUTPUT_DIR.rglob("*.json"))
    log(f"Found {len(json_files)} JSON files to rebuild")

    rebuilt = 0
    errors = 0

    for json_file in json_files:
        if json_file.name in ("index.json", "manifest.json"):
            continue

        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            log(f"  Skip {json_file}: {e}", "WARN")
            errors += 1
            continue

        content = data.get("content", "")
        if not content:
            continue

        topic = data.get("topic", data.get("base_concept", ""))
        category = data.get("category", "general")
        angle_id = data.get("angle", "what-is")
        base_concept = data.get("base_concept", topic)

        # Determine domain slug from path
        rel = json_file.relative_to(OUTPUT_DIR)
        parts = rel.parts
        domain_slug = None
        concept_slug = None

        # Check if structured folder: domain_structured/concept/angle.json
        if len(parts) >= 3 and parts[0].endswith("_structured"):
            domain_slug = parts[0].replace("_structured", "")
            concept_slug = parts[1]
        elif len(parts) >= 2:
            # Try category as domain
            domain_slug = parts[0] if parts[0] in DOMAIN_META else None
            concept_slug = slugify(base_concept)

        # Get list of all angles for this concept
        all_angles = set()
        if domain_slug and concept_slug:
            concept_dir = json_file.parent
            for f in concept_dir.glob("*.json"):
                all_angles.add(f.stem)

        # Get all concepts for this domain
        all_concepts = []
        if domain_slug:
            domain_dir = OUTPUT_DIR / f"{domain_slug}_structured"
            if domain_dir.exists():
                all_concepts = [d.name for d in domain_dir.iterdir() if d.is_dir()]

        # Build canonical path
        canonical_path = None
        if domain_slug and concept_slug and angle_id:
            canonical_path = f"{domain_slug}/{concept_slug}/{angle_id}.html"

        page_title = data.get("title", get_page_title(topic))

        html = format_as_html(
            topic=topic,
            content=content,
            page_title=page_title,
            domain_slug=domain_slug,
            concept_slug=concept_slug,
            angle_id=angle_id,
            all_angles=all_angles if all_angles else None,
            canonical_path=canonical_path,
            all_concepts=all_concepts if all_concepts else None,
        )

        # Write HTML alongside JSON
        html_file = json_file.with_suffix(".html")
        html_file.write_text(html, encoding="utf-8")
        rebuilt += 1

    log(f"Rebuilt {rebuilt} HTML pages ({errors} errors)", "SUCCESS")
    return rebuilt


def regenerate_all_content(domain=None, count=None, delay=2):
    """Delete existing content and regenerate all pages with improved prompts.

    Args:
        domain: Only regenerate pages in this domain (e.g., 'economics'). None = all.
        count: Max pages to regenerate. None = all.
        delay: Seconds between API calls (rate limiting).
    """
    import time

    registry = load_angle_registry()
    if not registry:
        log("No angle registry found", "ERROR")
        return []

    angles = registry.get("angles", {})

    # Find all concept folders (domain/concept/angle.json)
    from templates import DOMAIN_META
    domain_slugs = list(DOMAIN_META.keys())

    targets = []
    for d_slug in sorted(domain_slugs):
        if domain and d_slug != domain:
            continue
        domain_dir = OUTPUT_DIR / d_slug
        if not domain_dir.exists():
            continue
        for concept_dir in sorted(domain_dir.iterdir()):
            if not concept_dir.is_dir():
                continue
            concept_slug = concept_dir.name
            concept_name = concept_slug.replace("-", " ")
            for angle_id in angles:
                json_file = concept_dir / f"{angle_id}.json"
                if json_file.exists():
                    targets.append((d_slug, concept_slug, concept_name, angle_id, json_file))

    if count:
        targets = targets[:count]

    if not targets:
        log("No pages found to regenerate", "WARN")
        return []

    log(f"Regenerating {len(targets)} pages...")
    print("=" * 60)

    results = []
    for i, (d_slug, concept_slug, concept_name, angle_id, json_file) in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] {d_slug}/{concept_slug}/{angle_id}")
        print("-" * 40)

        try:
            # Build topic string from angle
            angle_config = angles[angle_id]
            topic = get_angle_title(concept_name, angle_id)

            # Generate new content using improved prompts
            content = generate_content(topic)
            if not content:
                log(f"  No content generated, skipping", "WARN")
                continue

            word_count = len(content.split())
            log(f"  Generated {word_count} words", "SUCCESS")

            # Get all sibling concepts for related linking
            domain_dir = OUTPUT_DIR / d_slug
            all_concepts = [d.name for d in domain_dir.iterdir() if d.is_dir()] if domain_dir.exists() else []
            all_angles = [f.stem for f in json_file.parent.glob("*.json")]

            page_title = get_angle_title(concept_name, angle_id)
            canonical_path = f"{d_slug}/{concept_slug}/{angle_id}.html"

            # Save JSON
            json_data = format_as_json(topic, content, d_slug, angle_id=angle_id, base_concept=concept_name)
            json_file.write_text(json_data, encoding="utf-8")

            # Save HTML
            html = format_as_html(
                topic=topic,
                content=content,
                page_title=page_title,
                domain_slug=d_slug,
                concept_slug=concept_slug,
                angle_id=angle_id,
                all_angles=all_angles,
                canonical_path=canonical_path,
                all_concepts=all_concepts,
            )
            json_file.with_suffix(".html").write_text(html, encoding="utf-8")

            # Save MD
            md = format_as_markdown(topic, content, page_title=page_title)
            json_file.with_suffix(".md").write_text(md, encoding="utf-8")

            results.append(f"{d_slug}/{concept_slug}/{angle_id}")

        except Exception as e:
            log(f"  Failed: {e}", "ERROR")

        if i < len(targets):
            time.sleep(delay)

    print("\n" + "=" * 60)
    log(f"Regenerated {len(results)}/{len(targets)} pages", "SUCCESS")
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
    parser.add_argument("--provider", type=str, choices=["groq", "grok", "gemini"], help="AI provider to use (default: auto-detect)")
    parser.add_argument("--list-topics", action="store_true", help="List all available topics")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--self-propagate", action="store_true", help="Run self-propagating mode")
    parser.add_argument("--auto-publish", action="store_true", help="Auto-commit and push to Git")
    parser.add_argument("--show-pending", action="store_true", help="Show pending discovered topics")
    parser.add_argument("--show-calculators", action="store_true", help="List topics with calculators")

    # Canonical Expansion (Upgrade 1)
    parser.add_argument("--expand-topics", action="store_true", help="Show canonical expansion statistics")
    parser.add_argument("--show-expanded", type=str, help="Show all angles for a specific topic")
    parser.add_argument("--generate-expanded", action="store_true", help="Generate from expanded topic list")

    # Concept Graph (Upgrade 2)
    parser.add_argument("--build-graph", action="store_true", help="Build concept graph using AI")
    parser.add_argument("--show-graph", action="store_true", help="Show concept graph")
    parser.add_argument("--graph-topic", type=str, help="Show graph for specific topic")
    parser.add_argument("--graph-comparisons", action="store_true", help="Show comparison pairs from graph")

    # System status
    parser.add_argument("--status", action="store_true", help="Show system status and capabilities")
    parser.add_argument("--detect-type", type=str, help="Show detected page type for a topic")

    # Completeness tracking (Upgrade 4)
    parser.add_argument("--completeness", action="store_true", help="Show completeness dashboard with all 4 metrics")
    parser.add_argument("--gaps", action="store_true", help="Show what's missing and next actions")

    # Domain closure (canonical concepts)
    parser.add_argument("--domain-status", type=str, help="Show closure status for a domain (e.g., finance)")
    parser.add_argument("--list-canonical", type=str, help="List all canonical concepts for a domain")

    # Maintenance
    parser.add_argument("--rerender", action="store_true", help="Re-render HTML from existing JSON files (fixes markdown conversion)")
    parser.add_argument("--restructure", action="store_true", help="Restructure into concept folders with canonical angle names")
    parser.add_argument("--dry-run", action="store_true", help="Show what restructure would do without making changes")
    parser.add_argument("--rebuild-html", action="store_true", help="Rebuild all HTML from JSON with new template features (TOC, cross-refs, meta)")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate ALL content with improved prompts (re-calls AI)")
    parser.add_argument("--domain", type=str, help="Filter regeneration to specific domain (e.g., economics)")

    # Closure tracking (per-concept completion)
    parser.add_argument("--closure-report", action="store_true", help="Show per-concept completion status (uses strict 8-angle registry)")
    parser.add_argument("--concept-status", type=str, help="Show completion status for a specific concept")

    args = parser.parse_args()

    # =========================================================================
    # SYSTEM STATUS
    # =========================================================================
    if args.status:
        log_data = load_generated_log()
        generated_count = len(log_data.get("generated", []))
        pending = load_pending_topics()
        graph = load_concept_graph()

        # Count base topics
        base_count = sum(len(topics) for cat, topics in TOPIC_CATEGORIES.items()
                        if cat not in ["comparisons", "classifications"])
        comparison_count = len(TOPIC_CATEGORIES.get("comparisons", []))
        classification_count = len(TOPIC_CATEGORIES.get("classifications", []))
        expanded_count = count_expanded_topics()

        print("=" * 60)
        print("KNOWLEDGE FACTORY STATUS")
        print("=" * 60)

        print("\n[TOPIC COVERAGE]")
        print(f"  Base topics:           {base_count}")
        print(f"  Comparisons:           {comparison_count}")
        print(f"  Classifications:       {classification_count}")
        print(f"  Expansion angles:      {len(CANONICAL_EXPANSIONS)}")
        print(f"  -----------------------------")
        print(f"  TOTAL POSSIBLE:        {expanded_count} pages")

        print("\n[GENERATION PROGRESS]")
        print(f"  Already generated:     {generated_count}")
        print(f"  Pending (discovered):  {len(pending)}")
        print(f"  Remaining:             {expanded_count - generated_count}")
        print(f"  Progress:              {generated_count/expanded_count*100:.1f}%")

        print("\n[CONCEPT GRAPH]")
        print(f"  Concepts mapped:       {len(graph)}")
        if graph:
            total_children = sum(len(g.get("children", [])) for g in graph.values())
            total_comparisons = sum(len(g.get("comparisons", [])) for g in graph.values())
            print(f"  Child topics:          {total_children}")
            print(f"  Comparison pairs:      {total_comparisons // 2}")

        print("\n[PAGE TYPES SUPPORTED]")
        print("  - Definition (what is X)")
        print("  - How it works (mechanism)")
        print("  - Why it matters (importance)")
        print("  - Examples (concrete illustrations)")
        print("  - Misconceptions (myth busting)")
        print("  - Beginner guide (intro)")
        print("  - Comparison (X vs Y)")
        print("  - Classification (types/parts/stages)")

        print("\n" + "=" * 60)

    elif args.detect_type:
        # Show detected page type
        topic = args.detect_type
        page_type = detect_page_type(topic)
        base_topic = extract_base_topic(topic)
        title = get_page_title(topic)

        print(f"\nTopic:      {topic}")
        print(f"Page type:  {page_type}")
        print(f"Base topic: {base_topic}")
        print(f"Title:      {title}")

    # =========================================================================
    # MAINTENANCE - Re-render HTML from JSON
    # =========================================================================
    elif args.rebuild_html:
        count = rebuild_all_html()
        print(f"\nRebuilt {count} HTML pages with new template features.")

    elif args.regenerate:
        results = regenerate_all_content(
            domain=args.domain,
            count=args.count,
        )
        print(f"\nRegenerated {len(results)} pages with improved prompts.")

    # =========================================================================
    elif args.rerender:
        import json
        import re
        category = args.category
        if not category:
            print("Error: --rerender requires --category")
            sys.exit(1)

        category_dir = OUTPUT_DIR / category
        if not category_dir.exists():
            print(f"Error: Category directory not found: {category_dir}")
            sys.exit(1)

        # Find JSON files recursively (handles both flat and concept-folder structures)
        json_files = list(category_dir.glob("**/*.json"))
        print(f"Found {len(json_files)} JSON files in {category}")
        print("Re-rendering HTML files with correct titles...")

        # Canonical angles (filename in concept folder structure)
        canonical_angles = {
            'what-is', 'how-it-works', 'what-it-depends-on', 'what-affects-it',
            'types-of', 'example-of', 'common-misconceptions-about', 'vs'
        }

        # Old flat file patterns to detect angle and extract base concept
        flat_patterns = [
            (r'^what-(.+)-depends-on$', 'what-it-depends-on', lambda m: m.group(1)),
            (r'^what-affects-(.+)$', 'what-affects-it', lambda m: m.group(1)),
            (r'^how-does-(.+)-work$', 'how-it-works', lambda m: m.group(1)),
            (r'^types-of-(.+)$', 'types-of', lambda m: m.group(1)),
            (r'^examples-of-(.+)$', 'example-of', lambda m: m.group(1)),
            (r'^common-misconceptions-about-(.+)$', 'common-misconceptions-about', lambda m: m.group(1)),
            (r'^(.+)-vs$', 'vs', lambda m: m.group(1)),
        ]

        rerendered = 0
        for json_path in json_files:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                topic = data.get("topic", "")
                content = data.get("content", "")

                if not topic or not content:
                    continue

                filename = json_path.stem
                parent_folder = json_path.parent.name

                # Check if this is concept folder structure (file is an angle name)
                if filename in canonical_angles:
                    angle_id = filename
                    base_concept = parent_folder
                else:
                    # Fall back to flat file pattern matching
                    angle_id = "what-is"  # default
                    base_concept = filename

                    for pattern, angle, extractor in flat_patterns:
                        match = re.match(pattern, filename)
                        if match:
                            angle_id = angle
                            base_concept = extractor(match)
                            break

                # Get correct title for this angle
                page_title = get_angle_title(base_concept, angle_id)

                # Re-generate HTML with correct title
                html_content = format_as_html(topic, content, page_title=page_title)
                html_path = json_path.with_suffix(".html")
                html_path.write_text(html_content, encoding="utf-8")

                # Also update markdown
                md_content = format_as_markdown(topic, content, page_title=page_title)
                md_path = json_path.with_suffix(".md")
                md_path.write_text(md_content, encoding="utf-8")

                # Update JSON with angle info
                data["angle"] = angle_id
                data["base_concept"] = base_concept
                data["title"] = page_title
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                rerendered += 1

                if rerendered % 25 == 0:
                    print(f"  Re-rendered {rerendered}/{len(json_files)}...")

            except Exception as e:
                print(f"  Error with {json_path.name}: {e}")

        print(f"\nRe-rendered {rerendered} HTML files with correct titles.")

    # =========================================================================
    # RESTRUCTURE INTO CONCEPT FOLDERS
    # =========================================================================
    elif args.restructure:
        import re
        import shutil

        category = args.category
        if not category:
            print("Error: --restructure requires --category")
            sys.exit(1)

        dry_run = args.dry_run
        category_dir = OUTPUT_DIR / category

        if not category_dir.exists():
            print(f"Error: Category directory not found: {category_dir}")
            sys.exit(1)

        # Load angle registry
        registry = load_angle_registry()
        if not registry:
            print("Error: No angle registry found")
            sys.exit(1)

        # Mapping from old file patterns to new angle names
        angle_mappings = [
            (r'^how-does-(.+)-work$', 'how-it-works', lambda m: m.group(1)),
            (r'^what-(.+)-depends-on$', 'what-it-depends-on', lambda m: m.group(1)),
            (r'^what-affects-(.+)$', 'what-affects-it', lambda m: m.group(1)),
            (r'^types-of-(.+)$', 'types-of', lambda m: m.group(1)),
            (r'^examples-of-(.+)$', 'example-of', lambda m: m.group(1)),
            (r'^common-misconceptions-about-(.+)$', 'common-misconceptions-about', lambda m: m.group(1)),
            (r'^(.+)-vs-(.+)$', 'vs', lambda m: m.group(1)),  # Keep first concept as folder
        ]

        # Deprecated patterns (will be quarantined)
        deprecated_patterns = [
            r'^why-(.+)-matters$',
            r'^what-(.+)-is-used-for$',
            r'^(.+)-for-beginners$',
            r'^parts-of-(.+)$',
            r'^stages-of-(.+)$',
        ]

        # Get all JSON files (source of truth)
        json_files = list(category_dir.glob("*.json"))
        print(f"Found {len(json_files)} files in {category}")

        # Create output structure
        restructured_dir = OUTPUT_DIR / f"{category}_structured"
        deprecated_dir = OUTPUT_DIR / f"{category}_deprecated"

        if not dry_run:
            restructured_dir.mkdir(exist_ok=True)
            deprecated_dir.mkdir(exist_ok=True)

        stats = {"moved": 0, "deprecated": 0, "base_def": 0, "unknown": 0}
        concepts_found = set()

        for json_path in json_files:
            stem = json_path.stem  # filename without extension
            concept = None
            new_angle = None
            is_deprecated = False

            # Check if deprecated
            for pattern in deprecated_patterns:
                match = re.match(pattern, stem)
                if match:
                    is_deprecated = True
                    concept = match.group(1)
                    break

            if is_deprecated:
                if dry_run:
                    print(f"  [DEPRECATED] {stem} -> {deprecated_dir.name}/")
                else:
                    # Move all formats to deprecated
                    for ext in ['.json', '.md', '.html']:
                        src = json_path.with_suffix(ext)
                        if src.exists():
                            shutil.move(str(src), str(deprecated_dir / src.name))
                stats["deprecated"] += 1
                continue

            # Check angle mappings
            for pattern, angle, extract_concept in angle_mappings:
                match = re.match(pattern, stem)
                if match:
                    concept = extract_concept(match)
                    new_angle = angle
                    break

            # If no pattern matched, it's likely a base definition
            if not concept:
                # Assume it's "what-is" (base definition)
                concept = stem
                new_angle = "what-is"
                stats["base_def"] += 1

            if concept and new_angle:
                concepts_found.add(concept)
                concept_dir = restructured_dir / concept

                if dry_run:
                    print(f"  {stem} -> {concept}/{new_angle}")
                else:
                    concept_dir.mkdir(exist_ok=True)
                    # Move all formats
                    for ext in ['.json', '.md', '.html']:
                        src = json_path.with_suffix(ext)
                        if src.exists():
                            dst = concept_dir / f"{new_angle}{ext}"
                            shutil.copy2(str(src), str(dst))
                stats["moved"] += 1
            else:
                if dry_run:
                    print(f"  [UNKNOWN] {stem}")
                stats["unknown"] += 1

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Restructure Summary:")
        print(f"  Concepts found:  {len(concepts_found)}")
        print(f"  Files moved:     {stats['moved']}")
        print(f"  Base definitions: {stats['base_def']}")
        print(f"  Deprecated:      {stats['deprecated']}")
        print(f"  Unknown:         {stats['unknown']}")

        if not dry_run:
            print(f"\nStructured output: {restructured_dir}")
            print(f"Deprecated files:  {deprecated_dir}")

            # Show sample concept
            sample = list(concepts_found)[0] if concepts_found else None
            if sample:
                sample_dir = restructured_dir / sample
                print(f"\nSample concept folder ({sample}):")
                for f in sorted(sample_dir.glob("*")):
                    print(f"  {f.name}")

    # =========================================================================
    # CLOSURE REPORT (Per-Concept Completion)
    # =========================================================================
    elif args.closure_report:
        category = args.category
        if not category:
            print("Error: --closure-report requires --category")
            sys.exit(1)

        report = get_category_completion_report(category)

        if "error" in report:
            print(f"Error: {report['error']}")
            sys.exit(1)

        print("=" * 70)
        print(f"CLOSURE REPORT: {category.upper()}")
        print("=" * 70)

        print(f"\n[SUMMARY]")
        print(f"  Total concepts:     {report['total_concepts']}")
        print(f"  Complete:           {report['complete_concepts']}")
        print(f"  Incomplete:         {len(report['incomplete_concepts'])}")
        print(f"  Completion:         {report['completion_percentage']:.1f}%")

        if report['missing_angles_summary']:
            print(f"\n[MISSING ANGLES SUMMARY]")
            for angle_id, count in sorted(report['missing_angles_summary'].items(), key=lambda x: -x[1]):
                print(f"  {angle_id}: missing in {count} concepts")

        if report['incomplete_concepts']:
            print(f"\n[INCOMPLETE CONCEPTS] (showing first 15)")
            for item in report['incomplete_concepts'][:15]:
                missing_str = ", ".join(item['missing_required'][:4])
                if len(item['missing_required']) > 4:
                    missing_str += f" (+{len(item['missing_required']) - 4} more)"
                print(f"  - {item['concept']}")
                print(f"    Required: {item['required_complete']}/{item['required_total']}")
                print(f"    Missing: {missing_str}")

        # Show what's needed for closure
        if report['completion_percentage'] < 100:
            total_missing = sum(report['missing_angles_summary'].values())
            print(f"\n[NEXT STEPS]")
            print(f"  {total_missing} pages needed for complete closure")
            print(f"  Run: python knowledge_pages.py --generate-expanded --category {category} --count {min(total_missing, 50)}")

    elif args.concept_status:
        concept = args.concept_status
        category = args.category or "finance"  # Default to finance

        # Load generated pages
        log_data = load_generated_log()
        generated = set()
        for entry in log_data.get("generated", []):
            if isinstance(entry, dict):
                generated.add(entry.get("slug", ""))
            else:
                generated.add(slugify(str(entry)))

        # Also check files on disk
        category_dir = OUTPUT_DIR / category
        if category_dir.exists():
            for f in category_dir.glob("*.json"):
                generated.add(f.stem)

        status = get_concept_completion_status(concept, category, generated)

        print("=" * 60)
        print(f"CONCEPT STATUS: {concept}")
        print("=" * 60)

        print(f"\n[REQUIRED ANGLES] ({status['required_complete']}/{status['required_total']})")
        for angle_id, angle_status in status['angles'].items():
            if angle_status['required']:
                marker = "[x]" if angle_status['exists'] else "[ ]"
                print(f"  {marker} {angle_id}: {angle_status['slug']}")

        print(f"\n[OPTIONAL ANGLES] ({status['optional_complete']}/{status['optional_total']})")
        for angle_id, angle_status in status['angles'].items():
            if not angle_status['required']:
                marker = "[x]" if angle_status['exists'] else "[ ]"
                print(f"  {marker} {angle_id}: {angle_status['slug']}")

        print(f"\n[STATUS]")
        if status['is_complete']:
            print("  COMPLETE - All required angles exist")
        else:
            missing = [a for a, s in status['angles'].items() if s['required'] and not s['exists']]
            print(f"  INCOMPLETE - Missing: {', '.join(missing)}")

    # =========================================================================
    # DOMAIN CLOSURE (Canonical Concepts)
    # =========================================================================
    elif args.domain_status:
        domain = args.domain_status.lower()
        status = get_domain_closure_status(domain)

        if "error" in status:
            print(f"Error: {status['error']}")
            print(f"Create file: canonical_concepts_{domain}.json")
        else:
            print("=" * 70)
            print(f"DOMAIN CLOSURE STATUS: {domain.upper()}")
            print("=" * 70)

            print(f"\n[BOUNDARY]")
            boundary = status.get("boundary", {})
            if boundary.get("includes"):
                print(f"  Includes: {', '.join(boundary['includes'][:5])}...")
            if boundary.get("excludes"):
                print(f"  Excludes: {', '.join(boundary['excludes'][:3])}...")

            print(f"\n[CANONICAL CONCEPTS]")
            print(f"  Total defined: {status['total_concepts']}")
            print(f"  Covered:       {status['covered']}")
            print(f"  Remaining:     {status['uncovered_count']}")
            print(f"  Progress:      {status['percentage']:.1f}%")

            print(f"\n[CLOSURE STATUS]")
            if status['is_closed']:
                print("  *** DOMAIN IS CLOSED ***")
                print("  No new concepts needed. Ready for licensing/embedding.")
            else:
                print(f"  NOT CLOSED - {status['uncovered_count']} concepts remaining")
                if status['uncovered_sample']:
                    print(f"\n  Sample uncovered concepts:")
                    for c in status['uncovered_sample'][:10]:
                        print(f"    - {c}")

            print("\n" + "=" * 70)

    elif args.list_canonical:
        domain = args.list_canonical.lower()
        data = load_canonical_concepts(domain)

        if not data:
            print(f"No canonical concepts file for: {domain}")
            print(f"Create file: canonical_concepts_{domain}.json")
        else:
            print(f"CANONICAL CONCEPTS: {domain.upper()}")
            print("=" * 60)

            for subcategory, concepts in data.get("concepts", {}).items():
                print(f"\n[{subcategory.upper()}] ({len(concepts)} concepts)")
                for c in concepts:
                    print(f"  - {c}")

            total = sum(len(c) for c in data.get("concepts", {}).values())
            print(f"\n{'=' * 60}")
            print(f"TOTAL: {total} canonical concepts")

    # =========================================================================
    # COMPLETENESS DASHBOARD (Upgrade 4)
    # =========================================================================
    elif args.completeness:
        # Show all 4 completeness metrics
        comp = calculate_completeness(category=args.category)

        print("=" * 70)
        print("UNIVERSAL KNOWLEDGE INDEX - COMPLETENESS DASHBOARD")
        if args.category:
            print(f"Category: {args.category}")
        print("=" * 70)

        # Metric 1: Concept Coverage
        cc = comp["concept_coverage"]
        status1 = "PASS" if cc["done"] else "FAIL"
        print(f"\n[METRIC 1] CONCEPT COVERAGE          {cc['percentage']:6.1f}%  [{status1}]")
        print(f"           Threshold: >= 98%")
        print(f"           Covered: {cc['covered']}/{cc['total']} base concepts")

        # Metric 2: Angle Coverage
        ac = comp["angle_coverage"]
        status2 = "PASS" if ac["done"] else "FAIL"
        print(f"\n[METRIC 2] ANGLE COVERAGE            {ac['percentage']:6.1f}%  [{status2}]")
        print(f"           Threshold: >= 95%")
        print(f"           Complete: {ac['fully_covered']}/{ac['total']} concepts have 10+ angles")
        if ac["top_gaps"]:
            gaps_str = ", ".join(f"{g[0]}({g[1]})" for g in ac["top_gaps"][:3])
            print(f"           Top gaps: {gaps_str}")

        # Metric 3: Graph Connectivity
        gc = comp["graph_connectivity"]
        status3 = "PASS" if gc["done"] else "FAIL"
        print(f"\n[METRIC 3] GRAPH CONNECTIVITY        {100-gc['orphan_percentage']:6.1f}%  [{status3}]")
        print(f"           Threshold: <= 2% orphans")
        print(f"           Nodes: {gc['total_nodes']}, Orphans: {gc['orphans']}")

        # Metric 4: Question Coverage
        qc = comp["question_coverage"]
        status4 = "PASS" if qc["done"] else "FAIL"
        print(f"\n[METRIC 4] QUESTION COVERAGE         {qc['percentage']:6.1f}%  [{status4}]")
        print(f"           Threshold: >= 95%")
        print(f"           Resolved: {qc['resolved']}/{qc['total']} question-concept pairs")

        # Metric 5: Calculator Coverage
        calc = comp["calculator_coverage"]
        status5 = "PASS" if calc["done"] else "FAIL"
        print(f"\n[METRIC 5] CALCULATOR COVERAGE       {calc['percentage']:6.1f}%  [{status5}]")
        print(f"           Threshold: >= 95%")
        print(f"           Covered: {calc['covered']}/{calc['eligible']} calculator-eligible topics")
        if calc["missing"]:
            missing_str = ", ".join(m["concept"] for m in calc["missing"][:3])
            print(f"           Missing: {missing_str}")

        # Overall status
        print("\n" + "-" * 70)
        if comp["all_done"]:
            print("DOMAIN STATUS: *** COMPLETE ***")
            print("All 5 metrics pass. This domain is done.")
        else:
            passing = sum([cc["done"], ac["done"], gc["done"], qc["done"], calc["done"]])
            print(f"DOMAIN STATUS: IN PROGRESS ({passing}/5 metrics passing)")

        print("=" * 70)

    elif args.gaps:
        # Show what's missing and recommended actions
        comp = calculate_completeness(category=args.category)
        actions = get_next_actions(comp)

        print("=" * 70)
        print("KNOWLEDGE INDEX - GAPS & NEXT ACTIONS")
        if args.category:
            print(f"Category: {args.category}")
        print("=" * 70)

        # Show gaps per metric
        cc = comp["concept_coverage"]
        if cc["uncovered"]:
            print(f"\n[UNCOVERED CONCEPTS] ({len(cc['uncovered'])} shown)")
            for c in cc["uncovered"][:10]:
                print(f"  - {c}")

        ac = comp["angle_coverage"]
        if ac["partial"]:
            print(f"\n[INCOMPLETE ANGLE COVERAGE] ({len(ac['partial'])} concepts)")
            for p in ac["partial"][:5]:
                missing_str = ", ".join(p["missing"][:3])
                print(f"  - {p['concept']}: {p['angles']}/12 angles (missing: {missing_str})")

        gc = comp["graph_connectivity"]
        if gc["orphan_list"]:
            print(f"\n[ORPHAN NODES] ({gc['orphans']} total)")
            for o in gc["orphan_list"][:10]:
                print(f"  - {o}")

        qc = comp["question_coverage"]
        if qc["unresolved"]:
            print(f"\n[UNRESOLVED QUESTIONS] ({qc['total'] - qc['resolved']} total)")
            for q in qc["unresolved"][:10]:
                print(f"  - {q}")

        # Recommended actions
        print("\n" + "-" * 70)
        print("RECOMMENDED ACTIONS (in priority order):")
        print("-" * 70)
        for i, action in enumerate(actions, 1):
            print(f"\n{i}. {action['action']}")
            print(f"   Reason: {action['reason']}")
            print(f"   Command: python knowledge_pages.py {action.get('command', '')}")
            if action.get("targets"):
                print(f"   Targets: {', '.join(action['targets'][:3])}")
            if action.get("focus_angles"):
                print(f"   Focus on: {', '.join(action['focus_angles'])}")

        print("\n" + "=" * 70)

    elif args.list_categories:
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

    # =========================================================================
    # CANONICAL EXPANSION COMMANDS (Upgrade 1)
    # =========================================================================
    elif args.expand_topics:
        # Show expansion statistics
        base_count = sum(len(topics) for cat, topics in TOPIC_CATEGORIES.items()
                        if cat not in ["comparisons", "classifications"])
        comparison_count = len(TOPIC_CATEGORIES.get("comparisons", []))
        classification_count = len(TOPIC_CATEGORIES.get("classifications", []))

        expanded_count = count_expanded_topics()

        print("=" * 60)
        print("CANONICAL EXPANSION STATISTICS")
        print("=" * 60)
        print(f"\nBase topics (definition pages):     {base_count}")
        print(f"Comparison pages (X vs Y):          {comparison_count}")
        print(f"Classification pages:               {classification_count}")
        print(f"\nExpansion angles per topic:         {len(CANONICAL_EXPANSIONS)}")
        print(f"  - {', '.join(CANONICAL_EXPANSIONS)}")
        print(f"\nTOTAL POSSIBLE PAGES:               {expanded_count}")
        print(f"\nMultiplier: {expanded_count / base_count:.1f}x")

    elif args.show_expanded:
        # Show all angles for a specific topic
        topic = args.show_expanded
        angles = expand_topic_to_angles(topic)
        print(f"\nCanonical angles for '{topic}':")
        print("-" * 40)
        for i, angle in enumerate(angles, 1):
            page_type = detect_page_type(angle)
            print(f"  {i}. {angle}")
            print(f"     Type: {page_type}")

    elif args.generate_expanded:
        # Generate from expanded topic list
        category = args.category
        if not category:
            print("Error: --generate-expanded requires --category")
            sys.exit(1)

        # Check actual files on disk, not the log (fixes cross-category duplicates)
        category_dir = OUTPUT_DIR / category
        log_data = load_generated_log()  # Still used for tracking

        # Get all expanded topics
        all_expanded = get_all_expanded_topics(categories=[category])

        # Build set of existing files
        existing_files = set()
        if category_dir.exists():
            for f in category_dir.glob("*.json"):
                existing_files.add(f.stem)

        # Filter out already generated by checking actual files
        pending = []
        for t in all_expanded:
            topic_slug = slugify(t["topic"])
            if topic_slug not in existing_files:
                pending.append(t)

        if not pending:
            log("All expanded topics already generated!", "SUCCESS")
        else:
            log(f"Found {len(pending)} expanded topics to generate")
            log(f"(out of {len(all_expanded)} total)")

            # Take requested count
            to_generate = pending[:args.count]

            results = []
            for i, topic_info in enumerate(to_generate, 1):
                topic = topic_info["topic"]
                cat = topic_info["category"]
                angle = topic_info["angle"]
                base_topic = topic_info.get("base_topic", topic)

                print(f"\n[{i}/{len(to_generate)}] {topic}")
                print(f"  Category: {cat}, Angle: {angle}")
                print("-" * 40)

                try:
                    result = generate_knowledge_page(
                        topic,
                        category=cat,
                        angle_id=angle,
                        base_concept=base_topic
                    )
                    results.append(result)
                    log_data["generated"].append(topic)
                    save_generated_log(log_data)

                except Exception as e:
                    log(f"Failed: {e}", "ERROR")
                    log_data.setdefault("failed", []).append({"topic": topic, "error": str(e)})
                    save_generated_log(log_data)

                # Rate limiting
                if i < len(to_generate):
                    import time
                    time.sleep(2)

            print("\n" + "=" * 60)
            log(f"Generated {len(results)}/{len(to_generate)} pages", "SUCCESS")

    # =========================================================================
    # CONCEPT GRAPH COMMANDS (Upgrade 2)
    # =========================================================================
    elif args.build_graph:
        # Build concept graph using AI
        topics = None
        if args.category:
            topics = TOPIC_CATEGORIES.get(args.category, [])

        if args.count and topics:
            topics = topics[:args.count]

        log("Building concept graph...")
        graph = build_concept_graph_for_topics(topics, use_ai=True)
        log(f"Graph now has {len(graph)} concepts", "SUCCESS")

    elif args.show_graph:
        # Show full concept graph
        graph = load_concept_graph()
        if not graph:
            print("Concept graph is empty. Run --build-graph first.")
        else:
            print(f"\nConcept Graph ({len(graph)} concepts)")
            print("=" * 60)
            for concept, relations in sorted(graph.items()):
                print(f"\n{concept.upper()}")
                if relations.get("parents"):
                    print(f"  Parents: {', '.join(relations['parents'])}")
                if relations.get("children"):
                    print(f"  Children: {', '.join(relations['children'])}")
                if relations.get("related"):
                    print(f"  Related: {', '.join(relations['related'])}")
                if relations.get("comparisons"):
                    print(f"  Compare with: {', '.join(relations['comparisons'])}")

    elif args.graph_topic:
        # Show graph for specific topic
        graph = load_concept_graph()
        topic = args.graph_topic.lower()

        if topic not in graph:
            print(f"'{topic}' not in graph. Building...")
            relations = generate_concept_relationships(topic)
            add_concept_to_graph(
                topic,
                parents=relations.get("parents", []),
                children=relations.get("children", []),
                related=relations.get("related", []),
                comparisons=relations.get("comparisons", []),
            )
            graph = load_concept_graph()

        print(f"\nConcept: {topic.upper()}")
        print("-" * 40)
        relations = graph.get(topic, {})
        print(f"Parents:     {', '.join(relations.get('parents', [])) or 'none'}")
        print(f"Children:    {', '.join(relations.get('children', [])) or 'none'}")
        print(f"Related:     {', '.join(relations.get('related', [])) or 'none'}")
        print(f"Compare:     {', '.join(relations.get('comparisons', [])) or 'none'}")

        # Show potential pages
        print(f"\nPotential pages from this concept:")
        all_related = (
            relations.get("children", []) +
            [f"{topic} vs {c}" for c in relations.get("comparisons", [])]
        )
        for r in all_related[:10]:
            print(f"  - {r}")

    elif args.graph_comparisons:
        # Show comparison pairs from graph
        pairs = get_comparison_pairs_from_graph()
        existing_comparisons = set(t.lower() for t in TOPIC_CATEGORIES.get("comparisons", []))

        print(f"\nComparison pairs from concept graph:")
        print("=" * 60)

        new_pairs = []
        for pair in pairs:
            if pair.lower() in existing_comparisons:
                print(f"  [EXISTS] {pair}")
            else:
                print(f"  [NEW]    {pair}")
                new_pairs.append(pair)

        print(f"\nTotal: {len(pairs)} pairs ({len(new_pairs)} new)")

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
