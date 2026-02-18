# Knowledge Asset Factory

**Zero-Touch Passive Income Pipeline**

Generates evergreen knowledge assets across multiple formats for silent distribution.

---

## The Core Insight

> "The most automated businesses don't sell creativity — they sell structure."

This pipeline generates:
- **Text pages** → SEO traffic → Ad revenue
- **Infographics** → Stock sites → Licensing
- **Printable PDFs** → Marketplaces → Direct sales
- **Structured JSON** → APIs → B2B licensing

All from the same knowledge base. One topic → multiple outputs.

---

## Quick Start

```bash
cd asset-generator

# Generate 10 knowledge assets
python pipeline.py --designs 10 --skip-upload

# Generate educational content only
python pipeline.py --designs 10 --educational-only

# Full pipeline with uploads
python pipeline.py --designs 10
```

---

## Opportunity Tiers (Ranked by Automation Potential)

### Tier 1: True "Set & Forget" (Best ROI)

| Opportunity | Format | Distribution | Revenue Model |
|-------------|--------|--------------|---------------|
| **Programmatic Knowledge Pages** | Text/HTML | Google SEO | Ads, Affiliates |
| **Printable Utilities** | PDF | Marketplaces | $5-20/pack |
| **Standalone Calculator Tools** | Web tools | SEO | Ads ($10-50 CPM) |

### Tier 2: High Automation

| Opportunity | Format | Distribution | Revenue Model |
|-------------|--------|--------------|---------------|
| **Educational Infographics** | PNG/PDF | Stock sites, POD | $0.50-5/download |
| **Structured Data Pages** | Tables/HTML | SEO | Ads |
| **Comparison Pages** | Text | SEO | Affiliates |

### Tier 3: Licensing (Advanced)

| Opportunity | Format | Distribution | Revenue Model |
|-------------|--------|--------------|---------------|
| **Knowledge APIs** | JSON | B2B | $99-999/year |
| **Educator Packs** | Bundles | Direct | $49-199/pack |
| **White-label Content** | Various | Licensing | Recurring |

---

## What This Pipeline Generates

### 1. Programmatic Knowledge Pages (NEW - Highest Value)

Evergreen SEO pages that answer one question each.

**Structure (never changes):**
```
H1: What is {{TOPIC}}?

1. One-sentence definition
2. Plain explanation (2-3 paragraphs)
3. Key components (bullets)
4. Common misconceptions (bullets)
5. Simple real-world example
6. One-sentence summary
```

**Example topics:**
- "What is compound interest?"
- "Explain photosynthesis simply"
- "Difference between ETF and mutual fund"

**Why this wins:**
- Google indexes text better than images
- Infinite long-tail keywords
- Zero design bottleneck
- Never expires

### 2. Printable Utilities (Underrated Goldmine)

Functional PDFs people USE, not just view.

**Types:**
- Checklists
- Trackers
- Worksheets
- Planners
- Assessment sheets
- Log templates

**Why this works:**
- Usefulness converts better than aesthetics
- Repeat purchases
- Bulk generation possible
- Zero support needed

### 3. Educational Infographics

Visual learning assets for classrooms.

**Categories:**
| Category | Examples | Languages |
|----------|----------|-----------|
| Life Cycles | Butterfly, Frog, Fly, Bee, Plant | EN, ES, FR |
| Science | Water cycle, Solar system, Photosynthesis | EN, ES, FR |
| Math | Times tables, Shapes, Fractions | EN, ES, FR |
| Language | Alphabet, Parts of speech | EN, ES, FR |

**Format:** 16:9 aspect ratio, 2K/4K resolution

### 4. Standalone Calculator Tool Pages (NEW - High CPM)

Full-page calculator tools at `/tools/` targeting transactional intent keywords ($10-50 CPM).

**Structure:** Calculator widget above the fold + AI-generated expert content below (how to use, formula, examples, FAQ).

**Categories:**
- Finance: Compound interest, mortgage, loan repayment, retirement, investment return, credit card payoff, emergency fund, net worth, DCA, APR/APY, inflation
- Tax: Income tax, salary after tax, capital gains, VAT, self-employment (with country variants for 12 countries)
- Math: Percentage, statistics, standard deviation, Pythagorean, circle area, volume, probability
- Business: Profit margin, break-even, ROI, markup
- Health: BMI, calorie
- Conversion: Unit, currency, temperature

**Total:** ~29 standalone + ~60 country variants = ~90 pages

```bash
# Generate all tool pages
python generate_tool_pages.py --generate-all

# Generate country variants (income tax, salary, etc. for 12 countries)
python generate_tool_pages.py --generate-country-variants

# Build tools landing page
python generate_tool_pages.py --build-index

# Rebuild HTML without API calls (from cached content)
python generate_tool_pages.py --rebuild-html

# Generate a single tool
python generate_tool_pages.py --generate-single compound-interest-calculator
```

### 5. Structured JSON Data (Future - Licensing)

Machine-readable knowledge for B2B.

```json
{
  "topic": "compound_interest",
  "definition": "...",
  "key_points": [],
  "examples": [],
  "misconceptions": []
}
```

**Buyers:** EdTech apps, LMS platforms, tutoring services

---

## Master Prompts (Production-Grade)

### Prompt 1: Knowledge Page (Text)

```
You are generating an evergreen educational reference page.

Topic: {{TOPIC}}

Rules:
- Neutral, factual, timeless
- 8th-grade reading level
- No opinions, dates, trends, current events
- No brand promotion

Structure:
1. One-sentence definition of {{TOPIC}}
2. Simple explanation (2-3 paragraphs)
3. Key components or principles (bullet list)
4. Common misconceptions (bullet list)
5. One simple real-world example
6. One-sentence summary

Constraints:
- 600-800 words
- Plain language
- No emojis
- Evergreen content only
```

### Prompt 2: Infographic (Visual)

```
Create an educational infographic: {{TITLE}}

Content: {{CONTENT}}

Style:
- Child-friendly, colorful
- Clear labels, professional design
- Suitable for classroom printing
- 16:9 aspect ratio
- High resolution
- All text in {{LANGUAGE}}
```

### Prompt 3: Printable Utility (PDF)

```
Generate a printable utility.

Type: {{CHECKLIST | TRACKER | WORKSHEET}}
Topic: {{TOPIC}}

Requirements:
- Black-and-white printing optimized
- Simple, minimal layout
- Functional and reusable
- No decorative language

Structure:
- Title
- Purpose (1 sentence)
- Instructions (3-5 steps)
- Main section (tables, checkboxes, blanks)
- Notes section
```

### Prompt 4: Structured Data (JSON)

```
Generate educational content in JSON format.

Topic: {{TOPIC}}

Output:
{
  "slug": "",
  "definition": "",
  "summary": "",
  "key_points": [],
  "examples": [],
  "misconceptions": [],
  "related_topics": []
}

Rules:
- Plain language
- No markup or emojis
- No opinions
- Deterministic structure
```

---

## Topic Categories (Evergreen)

### Science
- Life cycles (insects, animals, plants)
- Natural processes (water cycle, rock cycle)
- Body systems
- Physics basics
- Chemistry fundamentals

### Math
- Basic operations
- Fractions & decimals
- Geometry
- Statistics basics
- Financial math

### Finance (High Ad Revenue)
- Investment terms
- Banking concepts
- Tax basics
- Retirement planning
- Credit & debt

### Language
- Grammar rules
- Parts of speech
- Punctuation
- Vocabulary building

### General Knowledge
- How things work
- Comparisons (X vs Y)
- Definitions
- Processes

---

## Revenue Projections

### Content Volume vs Revenue

| Assets | Monthly Traffic | Ad Revenue | Licensing |
|--------|-----------------|------------|-----------|
| 100 pages | 1K-5K | $10-50 | - |
| 500 pages | 10K-50K | $100-500 | $0-200 |
| 2,000 pages | 50K-200K | $500-2K | $200-1K |
| 10,000 pages | 200K-1M | $2K-10K | $1K-5K |

### Timeline (Realistic)

| Phase | Timeframe | Status |
|-------|-----------|--------|
| Setup | Week 1-2 | Building |
| First 500 assets | Month 1-2 | Generating |
| Indexing begins | Month 2-3 | Waiting |
| First revenue | Month 3-6 | $10-100 |
| Compounding | Month 6-12 | $100-1K |
| Mature | Year 2+ | $1K-10K |

---

## Current Pipeline Status

| Component | Status | Notes |
|-----------|--------|-------|
| Knowledge page generator | ✅ Complete | 1,415 pages generated |
| Domain closure system | ✅ Complete | 4 domains closed |
| Calculator tool pages | ✅ Complete | 29 standalone + 60 country variants |
| Tool page generator | ✅ Complete | `generate_tool_pages.py` |
| Sitemap generator | ✅ Complete | Auto-generates sitemap.xml (incl. tools) |
| Self-expansion engine | 🔄 Documented | See `SELF_EXPANSION.md` |
| Infographic generator | ✅ Ready | Gemini + Stable Horde |
| Printable PDF generator | ❌ Pending | Future |
| JSON data exporter | ✅ Ready | Generated with each page |
| POD designs (micro-niche) | ✅ Ready | Bonus revenue stream |

### Domain Closure Status

| Domain | Concepts | Pages | Status |
|--------|----------|-------|--------|
| Finance | 25 | 175 | ✅ CLOSED |
| Life Obligations | 105 | 840 | ✅ CLOSED |
| Science | 25 | 200 | ✅ CLOSED |
| Math | 25 | 200 | ✅ CLOSED |
| Economics | 30 | 0 | 📋 QUEUED |
| Health | 40 | 0 | 📋 QUEUED |
| Psychology | 25 | 0 | 📋 QUEUED |
| Technology | 35 | 0 | 📋 QUEUED |

**Total: 1,415 pages across 4 closed domains**

See `DOMAIN_MANIFEST.json` for full roadmap.

### AI Providers

| Provider | Status | Best For |
|----------|--------|----------|
| Google Gemini | ⚠️ Need Pro | Infographics (16:9, 4K) |
| Stable Horde | ✅ Working | Backup images (free) |
| Ideogram | ✅ Fallback | Text-heavy designs |

---

## File Structure

```
asset-generator/
├── config.py                 # API keys, settings
├── knowledge_pages.py        # Main page generator (closure system)
├── calculators.py            # Calculator library (27 calculators)
├── templates.py              # Shared HTML/CSS templates (articles + tools)
├── generate_sitemap.py       # Sitemap and index generator
├── generate_tool_pages.py    # Tool page generation pipeline (NEW)
├── tool_registry.json        # Calculator tool definitions (NEW)
├── DOMAIN_MANIFEST.json      # Master domain tracker and roadmap
├── SELF_EXPANSION.md         # Self-expanding system architecture
├── angle_registry.json       # Frozen 8-angle registry
├── canonical_concepts_*.json # Domain boundary definitions
├── sitemap.xml               # Generated sitemap
├── generated_pages/
│   ├── index.html            # Homepage with navigation
│   ├── robots.txt            # Crawler instructions
│   ├── finance_structured/   # 25 concepts, 175 pages (CLOSED)
│   ├── life_obligations_structured/  # 105 concepts, 840 pages (CLOSED)
│   ├── science_structured/   # 25 concepts, 200 pages (CLOSED)
│   ├── math_structured/      # 25 concepts, 200 pages (CLOSED)
│   ├── {domain}_deprecated/  # Quarantined non-canonical pages
│   ├── tools/                # Standalone calculator tool pages (NEW)
│   │   ├── index.html        # Tools landing page
│   │   ├── {slug}/index.html # Individual tool pages
│   │   └── {slug}/{country}/index.html  # Country variants
│   └── tools_content/        # Cached AI content JSON (for rebuild)
├── pipeline.py               # Image orchestrator
├── design_generator.py       # AI image generation
├── educational_content.py    # Infographic topics
├── # PENDING (Self-Expansion)
├── domain_discovery.py       # Discovery engine (TO BUILD)
├── pending_domains.json      # Domain queue (TO BUILD)
├── expansion_rules.json      # Safety rails (TO BUILD)
├── domain_tree.json          # Pre-seeded tiers (TO BUILD)
└── .github/workflows/
    └── daily_expansion.yml   # Automation (TO BUILD)
```

---

## Next Steps (Priority Order)

### Phase 1: Foundation ✅ COMPLETE
- [x] Infographic generation working
- [x] Multi-language support (EN/ES/FR)
- [x] Gemini SDK integration
- [x] Knowledge page generator (text)
- [x] JSON data exporter
- [x] Close finance domain (175 pages)
- [x] Close life_obligations domain (840 pages)
- [x] Close science domain (200 pages)
- [x] Close math domain (200 pages)
- [x] Sitemap generator
- [x] Index page generator

### Phase 2: Self-Expansion (Current)
- [x] Document self-expansion architecture (`SELF_EXPANSION.md`)
- [ ] Build `domain_discovery.py` - Discovery engine
- [ ] Create `pending_domains.json` - Domain queue
- [ ] Create `expansion_rules.json` - Safety rails
- [ ] Create `domain_tree.json` - Pre-seeded tiers
- [ ] Create `.github/workflows/daily_expansion.yml` - Automation
- [ ] Deploy to Cloudflare Pages
- [ ] Submit sitemap to Google Search Console

### Phase 3: Scale
- [ ] Auto-close economics domain
- [ ] Auto-close health domain
- [ ] Auto-close psychology domain
- [ ] Auto-close technology domain
- [ ] Add Pagefind search
- [ ] Configure ad network (Ezoic)

### Phase 4: Synthesis
- [ ] Cross-domain linking
- [ ] Concept graph visualization
- [ ] API exposure for licensing
- [ ] Dataset licensing (B2B)

---

## The Key Principle

> **One logic engine → Thousands of outputs → Silent distribution**

Not: "What should I create next?"
But: "What rule system generates infinite useful assets?"

---

## What NOT To Do

❌ Social media posting
❌ Newsletters
❌ Community building
❌ Trend chasing
❌ Personal branding
❌ Custom client work

These kill automation.

---

## Commands Reference

```bash
# Generate assets
python pipeline.py --designs 10
python pipeline.py --designs 10 --skip-upload
python pipeline.py --educational-only

# Tool pages
python generate_tool_pages.py --generate-all              # All standalone tools
python generate_tool_pages.py --generate-country-variants  # Country-specific tax tools
python generate_tool_pages.py --build-index                # Tools landing page
python generate_tool_pages.py --rebuild-html               # Rebuild from cache (no API)
python generate_tool_pages.py --generate-single <slug>     # Single tool

# Sitemap & index
python generate_sitemap.py

# Reports
python pipeline.py --report

# Test components
python educational_content.py
python trend_scanner.py
```

---

## Configuration

### Required API Keys (config.py)

```python
# Primary (upgrade to Pro for production)
GOOGLE_API_KEY = "your-gemini-key"

# Fallback
IDEOGRAM_API_KEY = "your-key"
```

### Platform Credentials (for uploads)

```python
WIRESTOCK_EMAIL = ""
WIRESTOCK_PASSWORD = ""
REDBUBBLE_EMAIL = ""
REDBUBBLE_PASSWORD = ""
```

---

## Resources

- Google AI Studio: https://ai.google.dev/
- Stable Horde: https://stablehorde.net/
- Wirestock: https://wirestock.io/
- Teachers Pay Teachers: https://www.teacherspayteachers.com/

---

*Last updated: 2026-02-17*

*This is infrastructure, not a hack. Build once, wait for cash.*
