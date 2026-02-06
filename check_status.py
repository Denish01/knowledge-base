"""
Status Checker
Quick overview of pipeline health and performance.

Run: python check_status.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATS_FILE = BASE_DIR / "stats.json"
PIPELINE_LOG = BASE_DIR / "pipeline_log.json"
UPLOAD_LOG = BASE_DIR / "upload_log.json"
PENDING_UPLOADS = BASE_DIR / "pending_uploads.json"
GENERATED_DIR = BASE_DIR / "generated_designs"


def main():
    print("\n" + "=" * 60)
    print("ASSET GENERATOR STATUS")
    print(f"Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check stats
    if STATS_FILE.exists():
        stats = json.loads(STATS_FILE.read_text())
        print(f"\n[LIFETIME STATS]")
        print(f"  Total Generated: {stats.get('total_generated', 0)}")
        print(f"  Total Uploaded:  {stats.get('total_uploaded', 0)}")
        print(f"  Total Failed:    {stats.get('total_failed', 0)}")

        # Last 7 days
        runs = stats.get('runs', [])
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent = [r for r in runs if r.get('timestamp', '') > week_ago]

        if recent:
            print(f"\n[LAST 7 DAYS]")
            print(f"  Runs: {len(recent)}")
            print(f"  Generated: {sum(r.get('generated', 0) for r in recent)}")
            print(f"  Uploaded:  {sum(r.get('uploaded', 0) for r in recent)}")

    else:
        print("\n[!] No stats file found - pipeline hasn't run yet")

    # Check generated designs
    if GENERATED_DIR.exists():
        images = list(GENERATED_DIR.glob("*.png"))
        print(f"\n[GENERATED DESIGNS]")
        print(f"  Total files: {len(images)}")

        # Recent
        today = datetime.now().strftime("%Y%m%d")
        today_images = [f for f in images if today in f.name]
        print(f"  Today: {len(today_images)}")

    # Check pending uploads
    if PENDING_UPLOADS.exists():
        pending = json.loads(PENDING_UPLOADS.read_text())
        if pending:
            print(f"\n[PENDING MANUAL UPLOADS]")
            print(f"  Count: {len(pending)}")
            print(f"  Platforms: Redbubble (browser automation required)")

    # Check upload log
    if UPLOAD_LOG.exists():
        upload_log = json.loads(UPLOAD_LOG.read_text())
        by_platform = upload_log.get('stats', {}).get('by_platform', {})
        if by_platform:
            print(f"\n[UPLOADS BY PLATFORM]")
            for platform, count in by_platform.items():
                print(f"  {platform}: {count}")

    # Last run
    if PIPELINE_LOG.exists():
        log = json.loads(PIPELINE_LOG.read_text())
        if log:
            last = log[-1]
            print(f"\n[LAST RUN]")
            print(f"  Time: {last.get('timestamp', 'unknown')}")
            print(f"  Generated: {last.get('generated', 0)}/{last.get('target_designs', 0)}")
            print(f"  Uploaded: {last.get('uploaded', 0)}")

    # Config check
    try:
        from config import (
            OPENAI_API_KEY, IDEOGRAM_API_KEY, LEONARDO_API_KEY,
            REPLICATE_API_KEY, WIRESTOCK_EMAIL, PRINTFUL_API_KEY
        )

        print(f"\n[CONFIG STATUS]")
        providers = []
        if OPENAI_API_KEY:
            providers.append("OpenAI")
        if IDEOGRAM_API_KEY:
            providers.append("Ideogram")
        if LEONARDO_API_KEY:
            providers.append("Leonardo")
        if REPLICATE_API_KEY:
            providers.append("Replicate")

        if providers:
            print(f"  AI Providers: {', '.join(providers)}")
        else:
            print(f"  [!] No AI providers configured!")

        platforms = []
        if WIRESTOCK_EMAIL:
            platforms.append("Wirestock")
        if PRINTFUL_API_KEY:
            platforms.append("Printful")

        if platforms:
            print(f"  Platforms: {', '.join(platforms)}")
        else:
            print(f"  [*] No upload platforms configured (dry-run only)")

    except Exception as e:
        print(f"\n[!] Config error: {e}")

    print("\n" + "=" * 60)
    print("Run 'python pipeline.py --help' for commands")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
