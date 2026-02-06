"""
ASSET GENERATOR PIPELINE
Zero-Touch Passive Income System

Orchestrates:
1. Trend scanning for design ideas
2. AI design generation
3. Image post-processing (upscale, background removal)
4. Multi-platform upload
5. Performance tracking

Run: python pipeline.py --designs 10
Schedule: Daily via GitHub Actions
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from pathlib import Path

from config import (
    DESIGNS_PER_DAY, DESIGNS_PER_NICHE,
    PLATFORMS, AUTO_RETRY, MAX_RETRIES
)
from trend_scanner import generate_design_ideas, get_seasonal_trends
from design_generator import (
    DesignGenerator, generate_design_from_idea,
    upscale_image, remove_background
)
from platform_uploader import upload_to_all_platforms, add_to_pending

# Paths
BASE_DIR = Path(__file__).parent
PIPELINE_LOG = BASE_DIR / "pipeline_log.json"
STATS_FILE = BASE_DIR / "stats.json"


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "[i]", "SUCCESS": "[+]", "ERROR": "[!]", "WARN": "[*]"}.get(level, "")
    print(f"[{timestamp}] {prefix} {message}")


def load_stats():
    """Load pipeline statistics."""
    if STATS_FILE.exists():
        return json.loads(STATS_FILE.read_text())
    return {
        "total_generated": 0,
        "total_uploaded": 0,
        "total_failed": 0,
        "by_niche": {},
        "by_template": {},
        "by_provider": {},
        "runs": []
    }


def save_stats(stats):
    """Save pipeline statistics."""
    STATS_FILE.write_text(json.dumps(stats, indent=2))


def load_pipeline_log():
    """Load pipeline run history."""
    if PIPELINE_LOG.exists():
        return json.loads(PIPELINE_LOG.read_text())
    return []


def save_pipeline_log(log_data):
    """Save pipeline run history."""
    # Keep only last 100 runs
    log_data = log_data[-100:]
    PIPELINE_LOG.write_text(json.dumps(log_data, indent=2))


def run_pipeline(design_count=None, dry_run=False, skip_upload=False):
    """
    Run the complete asset generation pipeline.

    Args:
        design_count: Number of designs to generate (default: DESIGNS_PER_DAY)
        dry_run: If True, generate but don't upload
        skip_upload: If True, skip platform uploads

    Returns:
        Dict with run results
    """
    print("\n" + "=" * 70)
    print("ASSET GENERATOR PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    design_count = design_count or DESIGNS_PER_DAY
    stats = load_stats()
    pipeline_log = load_pipeline_log()

    run_result = {
        "timestamp": datetime.now().isoformat(),
        "target_designs": design_count,
        "generated": 0,
        "uploaded": 0,
        "failed": 0,
        "designs": []
    }

    # Step 1: Generate design ideas
    log(f"Generating {design_count} design ideas...")
    ideas = generate_design_ideas(count=design_count)

    if not ideas:
        log("No design ideas generated!", "ERROR")
        return run_result

    log(f"Generated {len(ideas)} design ideas", "SUCCESS")

    # Step 2: Initialize design generator
    generator = DesignGenerator()

    if not generator.providers:
        log("No AI providers available! Add API keys to config.py", "ERROR")
        return run_result

    # Step 3: Generate designs
    generated_designs = []

    for i, idea in enumerate(ideas, 1):
        print(f"\n{'-'*70}")
        log(f"DESIGN {i}/{len(ideas)}: {idea.get('type', 'custom')} - {idea.get('template', 'design')}")
        print("-" * 70)

        # Retry logic
        success = False
        for attempt in range(MAX_RETRIES if AUTO_RETRY else 1):
            try:
                result = generate_design_from_idea(generator, idea, index=i)

                if result and result.get('image_path'):
                    # Post-processing
                    image_path = result['image_path']

                    # Upscale for print quality
                    log("Upscaling for print quality...")
                    upscaled_path = upscale_image(image_path)
                    result['upscaled_path'] = upscaled_path

                    # Remove background for t-shirt designs
                    if idea.get('template') in ['typography', 'minimalist', 'vintage_badge']:
                        log("Removing background...")
                        nobg_path = remove_background(upscaled_path or image_path)
                        result['nobg_path'] = nobg_path

                    generated_designs.append(result)
                    run_result['generated'] += 1
                    success = True

                    # Update stats
                    stats['total_generated'] += 1
                    niche = idea.get('niche', 'other')
                    template = idea.get('template', 'other')
                    provider = result.get('provider', 'unknown')

                    stats['by_niche'][niche] = stats['by_niche'].get(niche, 0) + 1
                    stats['by_template'][template] = stats['by_template'].get(template, 0) + 1
                    stats['by_provider'][provider] = stats['by_provider'].get(provider, 0) + 1

                    break

            except Exception as e:
                log(f"Generation attempt {attempt + 1} failed: {e}", "WARN")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(5)  # Brief pause before retry

        if not success:
            run_result['failed'] += 1
            stats['total_failed'] += 1
            log("Design generation failed after all retries", "ERROR")

        # Rate limiting between designs
        if i < len(ideas):
            wait = random.randint(5, 15)
            log(f"Waiting {wait}s before next design...")
            time.sleep(wait)

    # Step 4: Upload to platforms
    if not dry_run and not skip_upload and generated_designs:
        print(f"\n{'='*70}")
        log("UPLOADING TO PLATFORMS")
        print("=" * 70)

        for design in generated_designs:
            try:
                # Use the best quality version available
                upload_path = (
                    design.get('nobg_path') or
                    design.get('upscaled_path') or
                    design.get('image_path')
                )

                design['image_path'] = upload_path

                results = upload_to_all_platforms(design)

                if results:
                    run_result['uploaded'] += 1
                    stats['total_uploaded'] += 1

                    design_record = {
                        'image_path': upload_path,
                        'idea': design.get('idea'),
                        'provider': design.get('provider'),
                        'platforms': [r.get('platform') for r in results]
                    }
                    run_result['designs'].append(design_record)

            except Exception as e:
                log(f"Upload failed: {e}", "ERROR")
                # Add to pending for manual upload
                add_to_pending(design, list(PLATFORMS.keys()))

            # Rate limiting between uploads
            time.sleep(random.randint(3, 8))

    elif skip_upload:
        log("Skipping uploads (--skip-upload flag)", "INFO")
        for design in generated_designs:
            run_result['designs'].append({
                'image_path': design.get('image_path'),
                'idea': design.get('idea'),
                'provider': design.get('provider'),
            })

    elif dry_run:
        log("Dry run - no uploads performed", "INFO")

    # Save stats and log
    stats['runs'].append({
        'timestamp': run_result['timestamp'],
        'generated': run_result['generated'],
        'uploaded': run_result['uploaded'],
        'failed': run_result['failed']
    })
    # Keep only last 30 days of runs
    stats['runs'] = stats['runs'][-30:]

    save_stats(stats)

    pipeline_log.append(run_result)
    save_pipeline_log(pipeline_log)

    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"  Target:     {design_count} designs")
    print(f"  Generated:  {run_result['generated']}")
    print(f"  Uploaded:   {run_result['uploaded']}")
    print(f"  Failed:     {run_result['failed']}")
    print(f"\n  Total all-time:")
    print(f"    Generated: {stats['total_generated']}")
    print(f"    Uploaded:  {stats['total_uploaded']}")
    print("=" * 70)

    return run_result


def check_seasonal_urgency():
    """Check if any seasonal events need urgent attention."""
    seasonal = get_seasonal_trends()

    urgent = [s for s in seasonal if s.get('priority', 0) > 30]

    if urgent:
        log(f"URGENT: {len(urgent)} seasonal events need designs!", "WARN")
        for event in urgent:
            log(f"  - {event['event']}: {event['days_until']} days away", "WARN")
        return urgent

    return []


def generate_weekly_report():
    """Generate a weekly performance report."""
    stats = load_stats()

    print("\n" + "=" * 70)
    print("WEEKLY PERFORMANCE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 70)

    # Last 7 days
    recent_runs = [r for r in stats.get('runs', [])[-7:]]
    total_generated = sum(r.get('generated', 0) for r in recent_runs)
    total_uploaded = sum(r.get('uploaded', 0) for r in recent_runs)
    total_failed = sum(r.get('failed', 0) for r in recent_runs)

    print(f"\nLast 7 Days:")
    print(f"  Runs: {len(recent_runs)}")
    print(f"  Generated: {total_generated}")
    print(f"  Uploaded: {total_uploaded}")
    print(f"  Failed: {total_failed}")
    print(f"  Success Rate: {total_generated / max(total_generated + total_failed, 1) * 100:.1f}%")

    print(f"\nAll-Time Stats:")
    print(f"  Total Generated: {stats.get('total_generated', 0)}")
    print(f"  Total Uploaded: {stats.get('total_uploaded', 0)}")

    print(f"\nBy Niche:")
    for niche, count in sorted(stats.get('by_niche', {}).items(), key=lambda x: x[1], reverse=True):
        print(f"  {niche}: {count}")

    print(f"\nBy Template:")
    for template, count in sorted(stats.get('by_template', {}).items(), key=lambda x: x[1], reverse=True):
        print(f"  {template}: {count}")

    print(f"\nBy AI Provider:")
    for provider, count in sorted(stats.get('by_provider', {}).items(), key=lambda x: x[1], reverse=True):
        print(f"  {provider}: {count}")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Asset Generator Pipeline')
    parser.add_argument('--designs', type=int, default=DESIGNS_PER_DAY,
                       help=f'Number of designs to generate (default: {DESIGNS_PER_DAY})')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate designs but don\'t upload')
    parser.add_argument('--skip-upload', action='store_true',
                       help='Skip platform uploads')
    parser.add_argument('--report', action='store_true',
                       help='Generate weekly report only')
    parser.add_argument('--check-seasonal', action='store_true',
                       help='Check for urgent seasonal events')

    args = parser.parse_args()

    if args.report:
        generate_weekly_report()
        return

    if args.check_seasonal:
        urgent = check_seasonal_urgency()
        if urgent:
            # Run extra designs for urgent events
            extra_count = min(sum(e['designs_needed'] for e in urgent) // 7, 20)
            log(f"Generating {extra_count} extra seasonal designs...")
            run_pipeline(design_count=extra_count, dry_run=args.dry_run, skip_upload=args.skip_upload)
        return

    run_pipeline(
        design_count=args.designs,
        dry_run=args.dry_run,
        skip_upload=args.skip_upload
    )


if __name__ == "__main__":
    main()
