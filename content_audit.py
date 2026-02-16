"""
Content Audit Script for 360Library
Scans generated pages, flags thin content, and produces audit reports.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "generated_pages"


def scan_pages():
    """Scan all generated JSON files and collect word counts."""
    pages = []
    for json_file in sorted(OUTPUT_DIR.rglob("*.json")):
        # Skip non-page files
        if json_file.name in ("index.json", "manifest.json"):
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        content = data.get("content", "")
        word_count = len(content.split()) if content else 0
        rel_path = json_file.relative_to(OUTPUT_DIR)

        pages.append({
            "path": str(rel_path),
            "topic": data.get("topic", data.get("base_concept", "")),
            "angle": data.get("angle", ""),
            "category": data.get("category", ""),
            "word_count": word_count,
            "generated_date": data.get("generated_date", ""),
        })

    return pages


def audit(thin_threshold=400):
    """Run full content audit.

    Args:
        thin_threshold: Pages below this word count are flagged as thin.

    Returns:
        dict with audit results
    """
    pages = scan_pages()
    if not pages:
        print("No pages found to audit.")
        return {}

    thin_pages = [p for p in pages if p["word_count"] < thin_threshold]
    word_counts = [p["word_count"] for p in pages]

    report = {
        "audit_date": datetime.now().isoformat(),
        "thin_threshold": thin_threshold,
        "total_pages": len(pages),
        "thin_pages_count": len(thin_pages),
        "thin_percentage": round(len(thin_pages) / len(pages) * 100, 1) if pages else 0,
        "avg_word_count": round(sum(word_counts) / len(word_counts)) if word_counts else 0,
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "thin_pages": sorted(thin_pages, key=lambda p: p["word_count"]),
        "by_category": {},
    }

    # Group stats by category
    cats = {}
    for p in pages:
        cat = p.get("category", "unknown")
        cats.setdefault(cat, []).append(p["word_count"])
    for cat, counts in sorted(cats.items()):
        thin_in_cat = sum(1 for c in counts if c < thin_threshold)
        report["by_category"][cat] = {
            "total": len(counts),
            "thin": thin_in_cat,
            "avg_words": round(sum(counts) / len(counts)) if counts else 0,
        }

    # Write reports
    report_file = BASE_DIR / "audit_report.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Audit report saved to: {report_file}")

    # Write noindex list
    noindex_file = BASE_DIR / "noindex_pages.txt"
    noindex_lines = [p["path"] for p in thin_pages]
    noindex_file.write_text("\n".join(noindex_lines), encoding="utf-8")
    print(f"Noindex list saved to: {noindex_file} ({len(noindex_lines)} pages)")

    # Print summary
    print(f"\n{'='*50}")
    print(f"360Library Content Audit")
    print(f"{'='*50}")
    print(f"Total pages: {report['total_pages']}")
    print(f"Thin pages (<{thin_threshold} words): {report['thin_pages_count']} ({report['thin_percentage']}%)")
    print(f"Average word count: {report['avg_word_count']}")
    print(f"Range: {report['min_word_count']} - {report['max_word_count']} words")
    print(f"\nBy category:")
    for cat, stats in report["by_category"].items():
        print(f"  {cat}: {stats['total']} pages, {stats['thin']} thin, avg {stats['avg_words']} words")

    if thin_pages:
        print(f"\nThinnest pages:")
        for p in thin_pages[:10]:
            print(f"  {p['word_count']:4d} words - {p['path']}")

    return report


if __name__ == "__main__":
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    audit(thin_threshold=threshold)
