# Self-Expanding Knowledge System

**Auto-Domain Discovery Architecture**

This document describes how the Universal Knowledge Index grows automatically without human intervention.

---

## Core Principle

> "The system discovers, prioritizes, and closes new domains autonomously."

The goal: **True passive income** where the system expands itself while you sleep.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SELF-EXPANSION ENGINE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │  DISCOVERY  │───▶│   SCORING   │───▶│   QUEUE     │───▶│ GENERATE │ │
│  │   ENGINE    │    │   ENGINE    │    │  MANAGER    │    │  ENGINE  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────────┘ │
│        │                  │                  │                  │      │
│        ▼                  ▼                  ▼                  ▼      │
│  - Google Trends    - Search Volume    - pending_domains.json  - Groq │
│  - Wikipedia        - Competition      - Priority ranking      - Pages│
│  - Related concepts - Monetization     - Status tracking       - JSON │
│  - Cross-domain     - Evergreen score  - Daily picks           - HTML │
│                                                                         │
│  SCHEDULE: Daily at 3 AM UTC via GitHub Actions                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component 1: Discovery Engine

### Sources for New Domains

| Source | Method | Output |
|--------|--------|--------|
| **Google Trends** | API queries for rising topics | Hot domains |
| **Wikipedia Categories** | Crawl category trees | Structured domains |
| **Related Concepts** | Extract from generated pages | Adjacent domains |
| **Cross-Domain Links** | Analyze "see also" patterns | Bridge domains |
| **Pre-Seeded Tiers** | Manual domain tree | Guaranteed expansion |

### Discovery Logic

```python
# Pseudo-code for discovery engine

def discover_new_domains():
    candidates = []

    # 1. Check pre-seeded tier (guaranteed)
    candidates += get_next_tier_domains()

    # 2. Extract from existing pages
    candidates += extract_related_topics()

    # 3. Query Google Trends (if API available)
    candidates += query_rising_topics()

    # 4. Crawl Wikipedia categories
    candidates += crawl_wikipedia_adjacent()

    # Filter and score
    scored = score_candidates(candidates)

    # Add to queue
    add_to_pending_queue(scored)
```

---

## Component 2: Scoring Engine

Every candidate domain gets a **priority score** (0-100) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Search Volume** | 25% | Monthly searches for core terms |
| **Competition** | 20% | How saturated is this niche? |
| **Monetization** | 25% | Ad RPM, affiliate potential |
| **Evergreen Score** | 20% | Will this be relevant in 5 years? |
| **Closure Feasibility** | 10% | Can we define 25+ concepts? |

### Scoring Formula

```
Priority = (Volume * 0.25) + (100 - Competition) * 0.20 +
           (Monetization * 0.25) + (Evergreen * 0.20) +
           (Feasibility * 0.10)
```

### Tier Bonuses

| Tier | Bonus | Reason |
|------|-------|--------|
| Pre-seeded (Tier 1-2) | +20 | Guaranteed high quality |
| Finance-adjacent | +15 | High RPM |
| Education-adjacent | +10 | Low competition |
| Health topics | +5 | High volume |

---

## Component 3: Domain Queue

### File: `pending_domains.json`

```json
{
  "queue": [
    {
      "domain": "economics",
      "priority": 92,
      "source": "pre-seeded",
      "concepts_estimated": 30,
      "discovered_date": "2026-02-06",
      "status": "pending",
      "notes": "Natural extension of finance"
    },
    {
      "domain": "health",
      "priority": 88,
      "source": "pre-seeded",
      "concepts_estimated": 40,
      "discovered_date": "2026-02-06",
      "status": "pending",
      "notes": "High search volume"
    },
    {
      "domain": "psychology",
      "priority": 75,
      "source": "related_concepts",
      "concepts_estimated": 25,
      "discovered_date": "2026-02-07",
      "status": "pending"
    }
  ],
  "processing": null,
  "completed": ["finance", "life_obligations", "science", "math"]
}
```

### Queue States

| State | Description |
|-------|-------------|
| `pending` | Waiting to be processed |
| `processing` | Currently generating pages |
| `completed` | All concepts closed |
| `blocked` | Needs manual review |

---

## Component 4: Expansion Rules (Safety Rails)

### Hard Limits

| Rule | Value | Reason |
|------|-------|--------|
| Max domains per day | 1 | Prevent runaway generation |
| Max concepts per domain | 50 | Keep domains focused |
| Min concepts per domain | 15 | Ensure domain viability |
| Max pages per day | 200 | API rate limits |
| Required angles | 6 | Closure standard |

### Quality Gates

Before a domain can be processed:

1. **Concept list must be defined** - No vague domains
2. **No duplicate concepts** - Check against all closed domains
3. **Evergreen validation** - No trending/temporal topics
4. **Monetization check** - Must have ad/affiliate potential

### Forbidden Patterns

```json
{
  "forbidden_domains": [
    "news",
    "current_events",
    "celebrity",
    "politics",
    "controversial_topics"
  ],
  "forbidden_keywords": [
    "breaking",
    "latest",
    "2024",
    "2025",
    "trending"
  ]
}
```

---

## Component 5: Daily Cycle

### GitHub Actions Workflow

```yaml
# .github/workflows/daily_expansion.yml

name: Daily Expansion

on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC daily
  workflow_dispatch:
    inputs:
      force_domain:
        description: 'Force specific domain'
        required: false

jobs:
  expand:
    runs-on: ubuntu-latest
    steps:
      # 1. Discovery Phase
      - name: Discover new domains
        run: python domain_discovery.py --discover

      # 2. Selection Phase
      - name: Pick next domain
        run: python domain_discovery.py --pick-next

      # 3. Generation Phase
      - name: Generate pages
        run: python knowledge_pages.py --generate-expanded --category $DOMAIN --count 200

      # 4. Closure Check
      - name: Check closure status
        run: python knowledge_pages.py --closure-report --category $DOMAIN

      # 5. Update Manifest
      - name: Update manifest
        run: python domain_discovery.py --update-manifest

      # 6. Regenerate Sitemap
      - name: Generate sitemap
        run: python generate_sitemap.py

      # 7. Commit & Deploy
      - name: Commit changes
        run: |
          git add .
          git commit -m "Auto-expand: $DOMAIN domain"
          git push
```

### Daily Flow

```
3:00 AM  │ Trigger
         │
3:01 AM  ├─▶ Run discovery engine
         │   └─▶ Find new domain candidates
         │
3:02 AM  ├─▶ Score candidates
         │   └─▶ Add to pending queue
         │
3:03 AM  ├─▶ Pick highest priority domain
         │   └─▶ Lock domain for processing
         │
3:05 AM  ├─▶ Generate canonical concepts (if needed)
         │   └─▶ Create canonical_concepts_{domain}.json
         │
3:10 AM  ├─▶ Generate pages (up to 200/day)
         │   └─▶ 6 angles × ~30 concepts = 180 pages
         │
3:40 AM  ├─▶ Check closure status
         │   └─▶ Mark domain as CLOSED if 100%
         │
3:41 AM  ├─▶ Update DOMAIN_MANIFEST.json
         │
3:42 AM  ├─▶ Regenerate sitemap.xml
         │
3:43 AM  ├─▶ Commit and push
         │
3:44 AM  └─▶ Deploy via GitHub Pages
         │
         ▼
         DONE - Repeat tomorrow
```

---

## Component 6: Pre-Seeded Domain Tree

### Tier 1: Foundation (Completed)

| Domain | Concepts | Pages | Status |
|--------|----------|-------|--------|
| finance | 25 | 175 | CLOSED |
| life_obligations | 105 | 840 | CLOSED |
| science | 25 | 200 | CLOSED |
| math | 25 | 200 | CLOSED |

### Tier 2: Expansion (Next)

| Domain | Priority | Est. Concepts | Source |
|--------|----------|---------------|--------|
| economics | 92 | 30 | finance-adjacent |
| health | 88 | 40 | high-volume |
| psychology | 75 | 25 | life-adjacent |
| technology | 70 | 35 | evergreen |

### Tier 3: Scale

| Domain | Priority | Est. Concepts | Source |
|--------|----------|---------------|--------|
| law | 65 | 30 | life_obligations-adjacent |
| business | 60 | 35 | finance-adjacent |
| environment | 55 | 25 | science-adjacent |
| nutrition | 50 | 30 | health-adjacent |

### Tier 4: Synthesis

| Domain | Priority | Est. Concepts | Source |
|--------|----------|---------------|--------|
| philosophy | 45 | 25 | psychology-adjacent |
| sociology | 40 | 25 | cross-domain |
| history | 35 | 50 | evergreen |
| geography | 30 | 30 | science-adjacent |

---

## File Structure (After Implementation)

```
asset-generator/
├── domain_discovery.py       # Discovery engine (NEW)
├── pending_domains.json      # Domain queue (NEW)
├── expansion_rules.json      # Safety rails (NEW)
├── domain_tree.json          # Pre-seeded tiers (NEW)
├── DOMAIN_MANIFEST.json      # Master status tracker
├── knowledge_pages.py        # Page generator
├── generate_sitemap.py       # Sitemap generator
└── .github/workflows/
    └── daily_expansion.yml   # Automation (NEW)
```

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Discovery Engine | NOT BUILT | `domain_discovery.py` |
| Scoring Engine | NOT BUILT | Part of discovery |
| Domain Queue | NOT BUILT | `pending_domains.json` |
| Expansion Rules | NOT BUILT | `expansion_rules.json` |
| Pre-Seeded Tree | NOT BUILT | `domain_tree.json` |
| Daily Workflow | NOT BUILT | `daily_expansion.yml` |
| Page Generator | COMPLETE | `knowledge_pages.py` |
| Closure Tracking | COMPLETE | Part of knowledge_pages |
| Sitemap Generator | COMPLETE | `generate_sitemap.py` |

---

## Revenue Impact

### Without Self-Expansion

```
4 domains × 25 concepts × 8 angles = 800 pages (fixed)
Monthly traffic: ~50K visits
Monthly revenue: ~$500
```

### With Self-Expansion

```
Year 1: 20 domains × 30 concepts × 8 angles = 4,800 pages
Year 2: 50 domains × 30 concepts × 8 angles = 12,000 pages
Year 3: 100 domains × 30 concepts × 8 angles = 24,000 pages

Projected traffic: 200K → 1M → 2.5M visits/year
Projected revenue: $2K → $10K → $25K/year
```

---

## The Key Insight

> **Manual work = Linear growth**
> **Automated expansion = Exponential growth**

The difference between $500/month forever and $10,000/month growing:

1. You never touch it again
2. It discovers new opportunities
3. It generates content automatically
4. It deploys itself
5. It compounds over time

---

## Next Steps

To activate self-expansion:

1. **Build `domain_discovery.py`** - The discovery engine
2. **Create `pending_domains.json`** - Initialize with Tier 2 domains
3. **Create `expansion_rules.json`** - Define safety rails
4. **Create `domain_tree.json`** - Pre-seed all tiers
5. **Create `.github/workflows/daily_expansion.yml`** - Automation
6. **Deploy** - Let it run forever

---

*Last updated: 2026-02-06*

*This is infrastructure for infinite passive growth.*
