"""
Platform Uploader
Automatically uploads designs to multiple POD and stock platforms.

Supported platforms:
- Wirestock (auto-distributes to Adobe Stock, Shutterstock, etc.)
- Redbubble (via browser automation)
- Printful (API)
- TeePublic (via browser automation)
"""

import os
import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path

from config import (
    WIRESTOCK_EMAIL, WIRESTOCK_PASSWORD,
    REDBUBBLE_EMAIL, REDBUBBLE_PASSWORD,
    PRINTFUL_API_KEY,
    PLATFORMS, NICHES
)

# Paths
BASE_DIR = Path(__file__).parent
UPLOAD_LOG = BASE_DIR / "upload_log.json"
PENDING_UPLOADS = BASE_DIR / "pending_uploads.json"


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "[i]", "SUCCESS": "[+]", "ERROR": "[!]", "WARN": "[*]"}.get(level, "")
    print(f"[{timestamp}] {prefix} {message}")


def load_upload_log():
    """Load upload history."""
    if UPLOAD_LOG.exists():
        return json.loads(UPLOAD_LOG.read_text())
    return {"uploads": [], "stats": {"total": 0, "by_platform": {}}}


def save_upload_log(log_data):
    """Save upload history."""
    UPLOAD_LOG.write_text(json.dumps(log_data, indent=2))


def generate_product_metadata(design_result):
    """
    Generate optimized titles, tags, and descriptions for marketplaces.

    Args:
        design_result: Dict with image_path, idea, prompt, etc.

    Returns:
        Dict with title, description, tags
    """
    idea = design_result.get('idea', {})
    niche = idea.get('niche', 'design')
    sub_niche = idea.get('sub_niche', '')
    template = idea.get('template', '')
    idea_type = idea.get('type', '')

    # Build title
    title_parts = []

    if sub_niche:
        title_parts.append(sub_niche.title())

    if template == 'typography':
        quote = idea.get('prompt_vars', {}).get('quote', '')
        if quote:
            title_parts.append(f'"{quote[:30]}"')
        title_parts.append("Typography Design")
    elif template == 'vintage_badge':
        title_parts.append("Vintage Retro Badge")
    elif template == 'minimalist':
        title_parts.append("Minimalist Art")
    elif template == 'retro_sunset':
        title_parts.append("Retro Sunset Design")
    else:
        title_parts.append("Design")

    # Add gift occasion
    occasions = ["Gift", "Birthday Gift", "Christmas Gift", "Funny Gift"]
    title_parts.append(random.choice(occasions))

    title = " - ".join(title_parts)[:140]  # Most platforms limit to 140 chars

    # Build tags
    tags = set()

    # Niche-specific tags
    niche_config = NICHES.get(niche, {})
    tags.update(niche_config.get('keywords', []))

    if sub_niche:
        tags.add(sub_niche)
        tags.add(f"{sub_niche} lover")
        tags.add(f"{sub_niche} gift")
        tags.add(f"funny {sub_niche}")

    # Template-specific tags
    template_tags = {
        'typography': ['typography', 'quote', 'saying', 'text design'],
        'vintage_badge': ['vintage', 'retro', 'badge', 'emblem', 'classic'],
        'minimalist': ['minimalist', 'simple', 'clean', 'modern', 'line art'],
        'retro_sunset': ['retro', 'sunset', '80s', 'synthwave', 'vaporwave'],
        'illustration': ['illustration', 'artwork', 'artistic', 'drawing'],
    }
    tags.update(template_tags.get(template, []))

    # Universal tags
    tags.update(['gift idea', 'unique gift', 'trendy', 'cool design'])

    # Seasonal tags if applicable
    if idea_type == 'seasonal':
        event = idea.get('event', '')
        if event:
            tags.add(event.lower())
            tags.add(f"{event.lower()} gift")

    # Product type tags
    tags.update(['t-shirt', 'shirt', 'tee', 'sticker', 'mug', 'poster'])

    # Limit to 13 tags (Redbubble limit)
    tags = list(tags)[:13]

    # Build description
    description = f"""
{title}

Perfect for anyone who loves {sub_niche or niche}! This unique design makes an amazing gift for:
- Birthdays
- Christmas
- Just because!

Features a high-quality {template.replace('_', ' ')} design that looks great on t-shirts, mugs, stickers, and more.

Click "Available Products" to see all the ways you can get this design!
    """.strip()

    return {
        'title': title,
        'description': description,
        'tags': tags,
        'niche': niche,
        'sub_niche': sub_niche,
    }


class WirestockUploader:
    """Upload to Wirestock (auto-distributes to multiple stock platforms)."""

    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        self.api_base = "https://api.wirestock.io/v1"

    def login(self):
        """Authenticate with Wirestock."""
        if not WIRESTOCK_EMAIL or not WIRESTOCK_PASSWORD:
            log("Wirestock credentials not configured", "WARN")
            return False

        try:
            # Note: Wirestock may require OAuth - this is a simplified example
            # You may need to get an API key from their developer portal
            response = self.session.post(
                f"{self.api_base}/auth/login",
                json={
                    "email": WIRESTOCK_EMAIL,
                    "password": WIRESTOCK_PASSWORD
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.session.headers['Authorization'] = f"Bearer {data.get('token', '')}"
                self.logged_in = True
                log("Wirestock: Logged in", "SUCCESS")
                return True
            else:
                log(f"Wirestock login failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            log(f"Wirestock login error: {e}", "ERROR")
            return False

    def upload(self, image_path, metadata):
        """Upload an image to Wirestock."""
        if not self.logged_in:
            if not self.login():
                return None

        try:
            # Generate stock-specific metadata
            stock_metadata = {
                'title': metadata['title'][:200],
                'description': metadata['description'][:500],
                'keywords': metadata['tags'],
                'category': 'illustrations',
                'auto_distribute': True,  # Distribute to all connected platforms
            }

            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, 'image/png')}
                response = self.session.post(
                    f"{self.api_base}/upload",
                    files=files,
                    data=stock_metadata,
                    timeout=120
                )

            if response.status_code in [200, 201]:
                result = response.json()
                log(f"Wirestock: Uploaded {metadata['title'][:30]}...", "SUCCESS")
                return {
                    'platform': 'wirestock',
                    'id': result.get('id'),
                    'url': result.get('url'),
                    'status': 'pending_review'
                }
            else:
                log(f"Wirestock upload failed: {response.status_code}", "ERROR")
                return None

        except Exception as e:
            log(f"Wirestock upload error: {e}", "ERROR")
            return None


class PrintfulUploader:
    """Upload to Printful via API."""

    def __init__(self):
        self.api_base = "https://api.printful.com"
        self.headers = {
            "Authorization": f"Bearer {PRINTFUL_API_KEY}",
            "Content-Type": "application/json"
        }

    def upload(self, image_path, metadata):
        """Upload a design to Printful's file library."""
        if not PRINTFUL_API_KEY:
            log("Printful API key not configured", "WARN")
            return None

        try:
            # First, upload the file
            with open(image_path, 'rb') as f:
                import base64
                image_data = base64.b64encode(f.read()).decode()

            response = requests.post(
                f"{self.api_base}/files",
                headers=self.headers,
                json={
                    "type": "default",
                    "url": f"data:image/png;base64,{image_data}",
                    "filename": Path(image_path).name,
                    "visible": True,
                },
                timeout=120
            )

            if response.status_code in [200, 201]:
                result = response.json()
                file_id = result.get('result', {}).get('id')

                log(f"Printful: Uploaded file {file_id}", "SUCCESS")
                return {
                    'platform': 'printful',
                    'file_id': file_id,
                    'preview_url': result.get('result', {}).get('preview_url'),
                    'status': 'uploaded'
                }
            else:
                log(f"Printful upload failed: {response.text[:100]}", "ERROR")
                return None

        except Exception as e:
            log(f"Printful upload error: {e}", "ERROR")
            return None


class RedbubbleUploader:
    """
    Upload to Redbubble.

    Note: Redbubble doesn't have a public API.
    This uses browser automation via Selenium.
    For production, consider using their bulk upload tool.
    """

    def __init__(self):
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            self.driver = webdriver.Chrome(options=options)
            return True

        except ImportError:
            log("Selenium not installed. Run: pip install selenium", "WARN")
            return False
        except Exception as e:
            log(f"WebDriver init failed: {e}", "ERROR")
            return False

    def login(self):
        """Log in to Redbubble."""
        if not REDBUBBLE_EMAIL or not REDBUBBLE_PASSWORD:
            log("Redbubble credentials not configured", "WARN")
            return False

        if not self.driver and not self._init_driver():
            return False

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            self.driver.get("https://www.redbubble.com/auth/login")
            time.sleep(2)

            # Find and fill login form
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(REDBUBBLE_EMAIL)

            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(REDBUBBLE_PASSWORD)

            # Submit
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_btn.click()

            time.sleep(3)

            # Check if logged in
            if "dashboard" in self.driver.current_url or "portfolio" in self.driver.current_url:
                log("Redbubble: Logged in", "SUCCESS")
                return True
            else:
                log("Redbubble: Login may have failed", "WARN")
                return False

        except Exception as e:
            log(f"Redbubble login error: {e}", "ERROR")
            return False

    def upload(self, image_path, metadata):
        """Upload a design to Redbubble."""
        # For production use, consider:
        # 1. Redbubble's bulk upload CSV tool
        # 2. Third-party services like Merch Titans, Productor

        log("Redbubble: Browser automation not fully implemented", "WARN")
        log("Tip: Use Redbubble's bulk upload tool or Merch Titans", "INFO")

        # Save to pending uploads for manual processing
        return {
            'platform': 'redbubble',
            'status': 'pending_manual',
            'image_path': image_path,
            'metadata': metadata,
        }

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()


def upload_to_all_platforms(design_result):
    """
    Upload a design to all enabled platforms.

    Args:
        design_result: Dict with image_path, idea, prompt, etc.

    Returns:
        List of upload results
    """
    results = []
    metadata = generate_product_metadata(design_result)
    image_path = design_result.get('image_path')

    if not image_path or not Path(image_path).exists():
        log(f"Image not found: {image_path}", "ERROR")
        return results

    log(f"Uploading: {metadata['title'][:50]}...")

    # Upload to each enabled platform
    if PLATFORMS.get('wirestock', {}).get('enabled'):
        uploader = WirestockUploader()
        result = uploader.upload(image_path, metadata)
        if result:
            results.append(result)

    if PLATFORMS.get('printful', {}).get('enabled'):
        uploader = PrintfulUploader()
        result = uploader.upload(image_path, metadata)
        if result:
            results.append(result)

    if PLATFORMS.get('redbubble', {}).get('enabled'):
        uploader = RedbubbleUploader()
        result = uploader.upload(image_path, metadata)
        if result:
            results.append(result)

    # Log results
    upload_log = load_upload_log()
    upload_log['uploads'].append({
        'timestamp': datetime.now().isoformat(),
        'image_path': image_path,
        'metadata': metadata,
        'results': results,
    })
    upload_log['stats']['total'] += 1

    for r in results:
        platform = r.get('platform', 'unknown')
        upload_log['stats']['by_platform'][platform] = \
            upload_log['stats']['by_platform'].get(platform, 0) + 1

    save_upload_log(upload_log)

    return results


def get_pending_uploads():
    """Get list of designs waiting for manual upload."""
    if PENDING_UPLOADS.exists():
        return json.loads(PENDING_UPLOADS.read_text())
    return []


def add_to_pending(design_result, platforms):
    """Add a design to pending uploads queue."""
    pending = get_pending_uploads()
    pending.append({
        'timestamp': datetime.now().isoformat(),
        'image_path': design_result.get('image_path'),
        'metadata': generate_product_metadata(design_result),
        'platforms': platforms,
    })
    PENDING_UPLOADS.write_text(json.dumps(pending, indent=2))


if __name__ == "__main__":
    # Test the uploader
    print("=" * 60)
    print("PLATFORM UPLOADER TEST")
    print("=" * 60)

    # Test metadata generation
    test_result = {
        'image_path': 'test.png',
        'idea': {
            'type': 'niche',
            'niche': 'pets',
            'sub_niche': 'dogs',
            'template': 'typography',
            'prompt_vars': {
                'quote': 'Life is better with a dog'
            }
        }
    }

    metadata = generate_product_metadata(test_result)
    print(f"\nTitle: {metadata['title']}")
    print(f"Tags: {', '.join(metadata['tags'])}")
    print(f"\nDescription:\n{metadata['description']}")
