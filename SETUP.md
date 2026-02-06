# Asset Generator - Setup Guide

## Zero-Touch Passive Income Pipeline

This system automatically generates AI designs and uploads them to multiple Print-on-Demand and stock media platforms.

---

## Quick Start (5 Minutes)

### 1. Get API Keys (Free/Low Cost)

| Service | Cost | Get Key |
|---------|------|---------|
| **Ideogram** | Free tier | https://ideogram.ai/ |
| **Leonardo.ai** | Free tier (150 credits/day) | https://leonardo.ai/ |
| **OpenAI** | Pay-per-use (~$0.04/image) | https://platform.openai.com/ |
| **Replicate** | Pay-per-use (~$0.003/image) | https://replicate.com/ |

**Minimum needed:** Just ONE of the above to start.

### 2. Configure `config.py`

```python
# Add at least one AI provider
OPENAI_API_KEY = "sk-..."  # OR
IDEOGRAM_API_KEY = "..."   # OR
LEONARDO_API_KEY = "..."   # OR
REPLICATE_API_KEY = "..."
```

### 3. Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Generate 3 test designs (no upload)
python pipeline.py --designs 3 --dry-run
```

### 4. Set Up GitHub Actions (Full Automation)

1. Push to GitHub
2. Go to Settings → Secrets → Actions
3. Add your API keys as secrets:
   - `OPENAI_API_KEY`
   - `IDEOGRAM_API_KEY`
   - etc.

4. Enable Actions in your repo
5. Done! Pipeline runs daily at 2 AM UTC

---

## Platform Setup

### Wirestock (Recommended - Easiest)

Wirestock auto-distributes to: Adobe Stock, Shutterstock, Getty, Freepik, etc.

1. Create account: https://wirestock.io/
2. Connect your stock platform accounts
3. Add credentials to `config.py`:
   ```python
   WIRESTOCK_EMAIL = "your@email.com"
   WIRESTOCK_PASSWORD = "your-password"
   ```

### Printful (For Etsy Integration)

1. Create Printful account: https://www.printful.com/
2. Get API key from Dashboard → Settings → API
3. Connect to Etsy store
4. Add to `config.py`:
   ```python
   PRINTFUL_API_KEY = "your-key"
   ```

### Redbubble (Manual Upload)

Redbubble doesn't have a public API. Options:
- Use their bulk upload tool (CSV)
- Use third-party tools like Merch Titans
- The pipeline saves designs to `generated_designs/` for manual upload

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         DAILY PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. TREND SCAN          2. GENERATE           3. UPLOAD         │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐   │
│  │ Google      │──────▶│ AI Image    │──────▶│ Wirestock   │   │
│  │ Trends      │       │ Generation  │       │ Printful    │   │
│  │ Seasonal    │       │ (DALL-E,    │       │ Redbubble   │   │
│  │ Calendar    │       │  Ideogram)  │       │ (pending)   │   │
│  └─────────────┘       └─────────────┘       └─────────────┘   │
│                                                                 │
│  SCHEDULE: Daily at 2 AM UTC                                    │
│  OUTPUT: 10 designs/day = 3,600/year                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Adjust Output Volume

```python
# config.py
DESIGNS_PER_DAY = 10  # Increase for more volume
```

### Enable/Disable Niches

```python
# config.py
NICHES = {
    "pets": {
        "enabled": True,  # Set to False to disable
        ...
    },
}
```

### Add Custom Niches

```python
NICHES["custom_niche"] = {
    "sub_niches": ["topic1", "topic2"],
    "styles": ["modern", "vintage"],
    "keywords": ["keyword1", "keyword2"],
    "enabled": True,
}
```

---

## Maintenance

### Zero-Touch Items

These require NO intervention:
- Daily design generation
- Trend scanning
- Platform uploads (via API)
- Stats tracking

### Monthly Review (Optional)

- Check `stats.json` for performance
- Review `pending_uploads.json` for manual uploads
- Run `python pipeline.py --report` for summary

### Seasonal Events

The pipeline auto-detects and prioritizes seasonal designs:
- Checks calendar 30-90 days ahead
- Increases output for major holidays
- Runs extra on Sundays via `--check-seasonal`

---

## Costs

### AI Generation (Per Design)

| Provider | Cost | Quality |
|----------|------|---------|
| Ideogram | Free (25/day) | Excellent for text |
| Leonardo | Free (150 credits) | Good |
| DALL-E 3 | $0.04 | Best quality |
| Replicate Flux | $0.003 | Fast |

### Monthly Estimate

| Designs/Day | AI Cost | Potential Revenue |
|-------------|---------|-------------------|
| 10 | $0-12/mo | $50-500/mo |
| 20 | $0-24/mo | $100-1000/mo |
| 50 | $0-60/mo | $250-2500/mo |

*Revenue varies significantly based on niche and design quality*

---

## Troubleshooting

### "No AI providers available"

Add at least one API key to `config.py`.

### "Generation failed after all retries"

- Check API key validity
- Check provider status page
- Reduce `DESIGNS_PER_DAY` temporarily

### Designs not uploading

- Check platform credentials
- Review `upload_log.json` for errors
- Manually upload from `generated_designs/`

---

## Files

```
asset-generator/
├── config.py           # Configuration & API keys
├── pipeline.py         # Main orchestrator
├── trend_scanner.py    # Finds trending topics
├── design_generator.py # AI image generation
├── platform_uploader.py # Multi-platform upload
├── requirements.txt    # Python dependencies
├── generated_designs/  # Output folder
├── stats.json          # Performance stats
├── pipeline_log.json   # Run history
└── .github/workflows/  # Automation
    └── generate.yml
```

---

## Support

- Check logs in `pipeline_log.json`
- Review GitHub Actions runs
- Generated designs saved even if upload fails
