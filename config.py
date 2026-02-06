"""
Asset Generator Configuration
Zero-Touch Passive Income Pipeline

Generates AI designs and distributes to multiple platforms:
- Print-on-Demand: Redbubble, TeePublic, Printful
- Stock Media: Wirestock (distributes to Adobe Stock, Shutterstock, etc.)
"""

# =============================================================================
# API KEYS - Fill these in once, never touch again
# =============================================================================

# OpenAI API (for DALL-E 3) - Get from https://platform.openai.com/
OPENAI_API_KEY = ""

# Ideogram API (free tier, great for text in images) - https://ideogram.ai/
IDEOGRAM_API_KEY = "pDJX3YhAXZQNO35UNS4qbxndUoYz76vpI_TDRmpFc5LXRMxq_T_rEzk_x6Fgo7GTc_pX-5EH-1p0gaZunTwEaw"

# Leonardo.ai API (free tier available) - https://leonardo.ai/
LEONARDO_API_KEY = ""

# Replicate API (for Flux, SDXL) - https://replicate.com/
REPLICATE_API_KEY = ""

# Google Gemini API (for Imagen 3) - https://ai.google.dev/
GOOGLE_API_KEY = "AIzaSyC61DGQuvngWBF0LpyFpNJwaXxeWkW_VZk"

# Google Trends (no API key needed - uses pytrends)

# Pinterest API (optional) - https://developers.pinterest.com/
PINTEREST_ACCESS_TOKEN = ""

# =============================================================================
# PLATFORM CREDENTIALS
# =============================================================================

# Wirestock (auto-distributes to multiple stock platforms)
# Get from: https://wirestock.io/
WIRESTOCK_EMAIL = ""
WIRESTOCK_PASSWORD = ""

# Redbubble (manual upload via browser automation)
REDBUBBLE_EMAIL = ""
REDBUBBLE_PASSWORD = ""

# Printful API - https://www.printful.com/api
PRINTFUL_API_KEY = ""

# Etsy API (for Printful integration) - https://www.etsy.com/developers/
ETSY_API_KEY = ""
ETSY_SHOP_ID = ""

# =============================================================================
# GENERATION SETTINGS
# =============================================================================

# Daily output targets
DESIGNS_PER_DAY = 10  # 10 designs/day = 300/month = 3,600/year
DESIGNS_PER_NICHE = 2  # Spread across niches

# Image settings
IMAGE_SIZE = "1024x1024"  # For DALL-E 3
UPSCALE_TO = "4096x4096"  # Final output resolution

# Quality control
MIN_QUALITY_SCORE = 0.7  # AI-assessed quality threshold
RETRY_FAILED = 3  # Retry failed generations

# =============================================================================
# NICHE CONFIGURATION - Proven POD niches
# =============================================================================

NICHES = {
    # High-volume evergreen niches
    "pets": {
        "sub_niches": ["dogs", "cats", "birds", "fish", "reptiles"],
        "styles": ["minimalist", "vintage", "cartoon", "realistic"],
        "keywords": ["pet lover", "dog mom", "cat dad", "fur baby"],
        "enabled": True,
    },
    "professions": {
        "sub_niches": ["nurse", "teacher", "engineer", "developer", "chef", "firefighter"],
        "styles": ["funny", "proud", "vintage", "minimalist"],
        "keywords": ["career pride", "job humor", "work life"],
        "enabled": True,
    },
    "hobbies": {
        "sub_niches": ["fishing", "gaming", "gardening", "hiking", "cooking", "reading"],
        "styles": ["retro", "modern", "illustrated", "typography"],
        "keywords": ["hobby lover", "weekend warrior", "enthusiast"],
        "enabled": True,
    },
    "family": {
        "sub_niches": ["mom", "dad", "grandma", "grandpa", "aunt", "uncle"],
        "styles": ["heartfelt", "funny", "vintage", "modern"],
        "keywords": ["family love", "parent life", "grandparent"],
        "enabled": True,
    },
    "motivation": {
        "sub_niches": ["success", "fitness", "mindset", "hustle", "gratitude"],
        "styles": ["bold", "minimalist", "artistic", "vintage"],
        "keywords": ["motivation", "inspiration", "mindset"],
        "enabled": True,
    },
}

# =============================================================================
# SEASONAL CALENDAR - Auto-schedules designs ahead of time
# =============================================================================

SEASONAL_CALENDAR = {
    # Format: "MM-DD": {"event": "name", "days_before": lead_time, "designs": count}
    "01-01": {"event": "New Year", "days_before": 30, "designs": 20},
    "02-14": {"event": "Valentine's Day", "days_before": 45, "designs": 30},
    "03-17": {"event": "St. Patrick's Day", "days_before": 30, "designs": 15},
    "04-01": {"event": "Easter", "days_before": 45, "designs": 20},  # Approximate
    "05-05": {"event": "Cinco de Mayo", "days_before": 30, "designs": 10},
    "05-12": {"event": "Mother's Day", "days_before": 60, "designs": 40},
    "06-16": {"event": "Father's Day", "days_before": 60, "designs": 40},
    "07-04": {"event": "4th of July", "days_before": 45, "designs": 25},
    "10-31": {"event": "Halloween", "days_before": 60, "designs": 50},
    "11-28": {"event": "Thanksgiving", "days_before": 45, "designs": 20},
    "12-25": {"event": "Christmas", "days_before": 90, "designs": 60},
}

# =============================================================================
# DESIGN TEMPLATES - Proven formulas that sell
# =============================================================================

DESIGN_TEMPLATES = {
    "typography": {
        "prompt_template": '"{quote}" in bold {style} typography, {color_scheme} colors, centered composition, transparent background, suitable for t-shirt printing',
        "product_types": ["t-shirt", "mug", "poster", "sticker"],
    },
    "illustration": {
        "prompt_template": "{style} illustration of {subject}, {mood} mood, {color_scheme} color palette, clean lines, suitable for merchandise",
        "product_types": ["t-shirt", "poster", "phone-case", "tote-bag"],
    },
    "vintage_badge": {
        "prompt_template": "vintage retro badge design for {subject}, distressed texture, {decade}s aesthetic, circular emblem, {color_scheme} colors, transparent background",
        "product_types": ["t-shirt", "sticker", "poster"],
    },
    "minimalist": {
        "prompt_template": "minimalist line art of {subject}, single continuous line, {color} on transparent background, modern aesthetic, vector style",
        "product_types": ["t-shirt", "mug", "poster", "sticker"],
    },
    "retro_sunset": {
        "prompt_template": "retro sunset design with {subject} silhouette, 80s synthwave aesthetic, gradient orange pink purple, palm trees optional, vintage vibes",
        "product_types": ["t-shirt", "poster", "sticker"],
    },
    "infographic": {
        "prompt_template": "Educational infographic poster: {title}. {content}. Style: {style}, {color_scheme} color palette. Child-friendly, clear labels, professional educational design, suitable for classroom printing, high resolution, no watermarks",
        "product_types": ["poster", "digital download", "printable"],
    },
}

# =============================================================================
# PLATFORM SETTINGS
# =============================================================================

PLATFORMS = {
    "wirestock": {
        "enabled": True,
        "auto_distribute": True,  # Let Wirestock handle distribution
        "categories": ["illustrations", "backgrounds", "abstract"],
    },
    "redbubble": {
        "enabled": True,
        "product_types": ["t-shirt", "sticker", "poster", "mug", "phone-case"],
        "markup_percentage": 20,  # Your profit margin
    },
    "printful": {
        "enabled": False,  # Enable when Etsy store is set up
        "sync_to_etsy": True,
    },
    "teepublic": {
        "enabled": True,
        "product_types": ["t-shirt", "sticker", "mug"],
    },
}

# =============================================================================
# AUTOMATION SETTINGS
# =============================================================================

# Schedule (GitHub Actions cron format)
SCHEDULE = {
    "daily_generation": "0 2 * * *",  # 2 AM UTC daily
    "trend_scan": "0 0 * * 0",  # Sundays at midnight
    "performance_report": "0 8 * * 1",  # Monday 8 AM UTC
}

# Self-healing
AUTO_RETRY = True
MAX_RETRIES = 3
ALERT_ON_FAILURE = True
ALERT_EMAIL = ""  # Optional: get email on failures

# Logging
LOG_LEVEL = "INFO"
KEEP_LOGS_DAYS = 30
