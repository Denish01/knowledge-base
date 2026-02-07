"""
Domain Discovery Engine
Self-expanding system that discovers, prioritizes, and closes new domains.

Features:
- Picks next domain from queue
- Generates canonical concept lists
- Tracks closure status
- Updates manifests automatically

This is the brain of the self-expanding knowledge system.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
import argparse

# Try to import Groq via OpenAI SDK
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False

# Try to import config
try:
    from config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Paths
BASE_DIR = Path(__file__).parent
PENDING_DOMAINS_FILE = BASE_DIR / "pending_domains.json"
DOMAIN_TREE_FILE = BASE_DIR / "domain_tree.json"
EXPANSION_RULES_FILE = BASE_DIR / "expansion_rules.json"
DOMAIN_MANIFEST_FILE = BASE_DIR / "DOMAIN_MANIFEST.json"
ANGLE_REGISTRY_FILE = BASE_DIR / "angle_registry.json"
OUTPUT_DIR = BASE_DIR / "generated_pages"


def load_json(filepath):
    """Load JSON file."""
    if filepath.exists():
        return json.loads(filepath.read_text(encoding="utf-8"))
    return None


def save_json(filepath, data):
    """Save JSON file with pretty formatting."""
    filepath.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def get_groq_client():
    """Initialize Groq client."""
    if not OPENAI_SDK_AVAILABLE:
        print("ERROR: OpenAI SDK not available. Install with: pip install openai")
        return None
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set in config.py or environment")
        return None
    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


def pick_next_domain():
    """Pick the highest priority domain from the queue."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        print("ERROR: pending_domains.json not found")
        return None

    # Check if already processing
    if pending.get("processing"):
        print(f"Already processing: {pending['processing']}")
        return pending["processing"]

    # Get pending domains sorted by priority
    queue = pending.get("queue", [])
    pending_domains = [d for d in queue if d.get("status") == "pending"]

    if not pending_domains:
        print("No pending domains in queue")
        return None

    # Sort by priority (highest first)
    pending_domains.sort(key=lambda x: x.get("priority", 0), reverse=True)
    next_domain = pending_domains[0]

    print(f"Next domain: {next_domain['domain']} (priority: {next_domain['priority']})")
    return next_domain["domain"]


def lock_domain(domain_name):
    """Lock a domain for processing."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        return False

    # Update status in queue
    for domain in pending.get("queue", []):
        if domain["domain"] == domain_name:
            domain["status"] = "processing"
            break

    pending["processing"] = domain_name
    save_json(PENDING_DOMAINS_FILE, pending)
    print(f"Locked domain: {domain_name}")
    return True


def unlock_domain(domain_name, new_status="completed"):
    """Unlock a domain after processing."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        return False

    # Update status in queue
    for domain in pending.get("queue", []):
        if domain["domain"] == domain_name:
            domain["status"] = new_status
            if new_status == "completed":
                domain["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            break

    # Clear processing
    if pending.get("processing") == domain_name:
        pending["processing"] = None

    # Add to completed list if successful
    if new_status == "completed":
        if domain_name not in pending.get("completed", []):
            pending.setdefault("completed", []).append(domain_name)

    save_json(PENDING_DOMAINS_FILE, pending)
    print(f"Unlocked domain: {domain_name} (status: {new_status})")
    return True


def generate_concepts_for_domain(domain_name):
    """Use AI to generate canonical concept list for a domain."""
    client = get_groq_client()
    if not client:
        return None

    # Load domain tree for context
    tree = load_json(DOMAIN_TREE_FILE)
    domain_info = None

    if tree:
        for tier_name, tier_data in tree.get("tiers", {}).items():
            domains = tier_data.get("domains", {})
            if domain_name in domains:
                domain_info = domains[domain_name]
                break

    subcategories = domain_info.get("subcategories", []) if domain_info else []
    concepts_target = domain_info.get("concepts_target", 25) if domain_info else 25

    prompt = f"""Generate a list of {concepts_target} canonical concepts for the domain: {domain_name}

Requirements:
- Each concept must be a single, specific, evergreen topic
- Use lowercase-hyphenated slugs (e.g., "compound-interest", "photosynthesis")
- No temporal/trending topics
- No brand names
- No controversial topics
- Focus on foundational, educational concepts

{"Subcategories to cover: " + ", ".join(subcategories) if subcategories else ""}

Output format (JSON array of objects):
[
  {{"concept": "concept-slug", "title": "Human Readable Title", "subcategory": "subcategory_name"}},
  ...
]

Return ONLY the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        concepts = json.loads(content)
        print(f"Generated {len(concepts)} concepts for {domain_name}")
        return concepts

    except Exception as e:
        print(f"ERROR generating concepts: {e}")
        return None


def save_canonical_concepts(domain_name, concepts):
    """Save canonical concepts file for a domain."""
    # Group by subcategory
    by_subcategory = {}
    for concept in concepts:
        subcat = concept.get("subcategory", "general")
        if subcat not in by_subcategory:
            by_subcategory[subcat] = []
        by_subcategory[subcat].append({
            "concept": concept["concept"],
            "title": concept["title"]
        })

    output = {
        "domain": domain_name,
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "total_concepts": len(concepts),
        "subcategories": by_subcategory
    }

    filepath = BASE_DIR / f"canonical_concepts_{domain_name}.json"
    save_json(filepath, output)
    print(f"Saved: {filepath}")
    return filepath


def check_domain_closure(domain_name):
    """Check if a domain has achieved closure (100% of required angles)."""
    registry = load_json(ANGLE_REGISTRY_FILE)
    if not registry:
        print("ERROR: angle_registry.json not found")
        return None

    required_angles = [
        angle_id for angle_id, config in registry.get("angles", {}).items()
        if config.get("required", False)
    ]

    # Check domain folder (try both with and without _structured suffix for compatibility)
    domain_dir = OUTPUT_DIR / domain_name
    if not domain_dir.exists():
        domain_dir = OUTPUT_DIR / f"{domain_name}_structured"
    if not domain_dir.exists():
        return {"closed": False, "concepts": 0, "pages": 0, "completion": 0}

    total_concepts = 0
    total_pages = 0
    complete_concepts = 0

    for concept_dir in domain_dir.iterdir():
        if not concept_dir.is_dir():
            continue

        total_concepts += 1
        concept_pages = 0
        concept_complete = True

        for angle_id in required_angles:
            angle_file = concept_dir / f"{angle_id}.json"
            if angle_file.exists():
                concept_pages += 1
            else:
                concept_complete = False

        # Count optional angles too
        for f in concept_dir.glob("*.json"):
            total_pages += 1

        if concept_complete:
            complete_concepts += 1

    completion = (complete_concepts / total_concepts * 100) if total_concepts > 0 else 0

    return {
        "closed": completion == 100,
        "concepts": total_concepts,
        "pages": total_pages,
        "completion": round(completion, 1),
        "complete_concepts": complete_concepts
    }


def update_manifest(domain_name, status_info):
    """Update DOMAIN_MANIFEST.json with domain status."""
    manifest = load_json(DOMAIN_MANIFEST_FILE)
    if not manifest:
        print("ERROR: DOMAIN_MANIFEST.json not found")
        return False

    # Update domain entry
    if domain_name in manifest.get("domains", {}):
        manifest["domains"][domain_name].update({
            "status": "CLOSED" if status_info["closed"] else "IN_PROGRESS",
            "concepts": status_info["concepts"],
            "pages": status_info["pages"],
            "canonical_file": f"canonical_concepts_{domain_name}.json"
        })
        if status_info["closed"]:
            manifest["domains"][domain_name]["closure_date"] = datetime.now().strftime("%Y-%m-%d")
    else:
        # Add new domain
        manifest.setdefault("domains", {})[domain_name] = {
            "status": "CLOSED" if status_info["closed"] else "IN_PROGRESS",
            "concepts": status_info["concepts"],
            "pages": status_info["pages"],
            "canonical_file": f"canonical_concepts_{domain_name}.json",
            "closure_date": datetime.now().strftime("%Y-%m-%d") if status_info["closed"] else None
        }

    # Update totals
    domains = manifest.get("domains", {})
    manifest["totals"] = {
        "domains_closed": sum(1 for d in domains.values() if d.get("status") == "CLOSED"),
        "domains_queued": sum(1 for d in domains.values() if d.get("status") in ["QUEUED", "IN_PROGRESS"]),
        "total_concepts": sum(d.get("concepts", 0) for d in domains.values()),
        "total_pages": sum(d.get("pages", 0) for d in domains.values())
    }

    manifest["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    save_json(DOMAIN_MANIFEST_FILE, manifest)
    print(f"Updated manifest for {domain_name}")
    return True


def get_all_known_domains():
    """Get all domains we know about (completed, processing, pending)."""
    known = set()

    # From pending_domains.json
    pending = load_json(PENDING_DOMAINS_FILE)
    if pending:
        for d in pending.get("queue", []):
            known.add(d["domain"].lower())
        for d in pending.get("completed", []):
            known.add(d.lower())

    # From DOMAIN_MANIFEST.json
    manifest = load_json(DOMAIN_MANIFEST_FILE)
    if manifest:
        for domain in manifest.get("domains", {}).keys():
            known.add(domain.lower())

    return known


def discover_new_domains(count=5):
    """Use AI to discover new domains that don't exist yet."""
    client = get_groq_client()
    if not client:
        return []

    known_domains = get_all_known_domains()
    print(f"Known domains ({len(known_domains)}): {', '.join(sorted(known_domains))}")

    prompt = f"""Suggest {count + 5} new knowledge domains for an educational encyclopedia website.

EXISTING DOMAINS (DO NOT SUGGEST THESE OR SYNONYMS):
{', '.join(sorted(known_domains))}

Requirements for new domains:
- Single-word or two-word domain names (e.g., "geography", "music-theory", "astronomy")
- Evergreen educational topics (not trending/temporal)
- High search volume potential
- Can be broken into 25-50 distinct concepts
- No overlap with existing domains
- No controversial topics
- No brand-specific content
- Suitable for a "What is X?" educational format

Output format (JSON array):
[
  {{"domain": "domain-slug", "priority": 50, "concepts_estimated": 30, "notes": "Brief description"}},
  ...
]

Priority scale: 40-60 (lower priority since auto-discovered)
Return ONLY the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        suggestions = json.loads(content)

        # Filter out any that somehow match existing domains
        new_domains = []
        for s in suggestions:
            domain_slug = slugify(s["domain"])
            if domain_slug not in known_domains and domain_slug.replace("-", "_") not in known_domains:
                s["domain"] = domain_slug
                new_domains.append(s)

        print(f"Discovered {len(new_domains)} new domains")
        return new_domains[:count]  # Return only requested count

    except Exception as e:
        print(f"ERROR discovering domains: {e}")
        return []


def add_domains_to_queue(new_domains):
    """Add newly discovered domains to the queue."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        pending = {"version": "1.0", "queue": [], "completed": [], "processing": None}

    known = get_all_known_domains()
    added = 0

    for domain_info in new_domains:
        domain_slug = domain_info["domain"]

        # Double-check not duplicate
        if domain_slug in known:
            print(f"  Skipping duplicate: {domain_slug}")
            continue

        new_entry = {
            "domain": domain_slug,
            "priority": domain_info.get("priority", 45),
            "source": "auto-discovered",
            "tier": 4,
            "concepts_estimated": domain_info.get("concepts_estimated", 25),
            "discovered_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "pending",
            "notes": domain_info.get("notes", "Auto-discovered domain")
        }

        pending["queue"].append(new_entry)
        known.add(domain_slug)
        added += 1
        print(f"  Added to queue: {domain_slug}")

    if added > 0:
        pending["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_json(PENDING_DOMAINS_FILE, pending)
        print(f"Added {added} new domains to queue")

    return added


def check_and_refill_queue(min_pending=3, refill_count=5):
    """Check if queue needs refilling and discover new domains if needed."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        return False

    # Count pending domains
    queue = pending.get("queue", [])
    pending_count = sum(1 for d in queue if d.get("status") == "pending")

    print(f"Pending domains in queue: {pending_count}")

    if pending_count >= min_pending:
        print(f"Queue has enough domains (>= {min_pending}). No refill needed.")
        return False

    print(f"Queue low (< {min_pending}). Discovering new domains...")

    # Discover new domains
    new_domains = discover_new_domains(count=refill_count)

    if new_domains:
        added = add_domains_to_queue(new_domains)
        return added > 0

    return False


def get_queue_status():
    """Get current queue status."""
    pending = load_json(PENDING_DOMAINS_FILE)
    if not pending:
        return None

    queue = pending.get("queue", [])
    completed = pending.get("completed", [])
    processing = pending.get("processing")

    status = {
        "pending": [d["domain"] for d in queue if d.get("status") == "pending"],
        "processing": processing,
        "completed": completed,
        "total_in_queue": len(queue)
    }

    return status


def print_status():
    """Print current expansion status."""
    print("\n" + "=" * 60)
    print("SELF-EXPANSION STATUS")
    print("=" * 60)

    status = get_queue_status()
    if status:
        print(f"\nProcessing: {status['processing'] or 'None'}")
        print(f"Pending: {', '.join(status['pending'][:5])}{'...' if len(status['pending']) > 5 else ''}")
        print(f"Completed: {', '.join(status['completed'])}")
        print(f"Total in queue: {status['total_in_queue']}")

    manifest = load_json(DOMAIN_MANIFEST_FILE)
    if manifest:
        totals = manifest.get("totals", {})
        print(f"\nTotal domains closed: {totals.get('domains_closed', 0)}")
        print(f"Total pages: {totals.get('total_pages', 0)}")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Domain Discovery Engine")

    parser.add_argument("--status", action="store_true",
                        help="Show current expansion status")
    parser.add_argument("--pick-next", action="store_true",
                        help="Pick and display next domain to process")
    parser.add_argument("--lock", type=str, metavar="DOMAIN",
                        help="Lock a domain for processing")
    parser.add_argument("--unlock", type=str, metavar="DOMAIN",
                        help="Unlock a domain after processing")
    parser.add_argument("--generate-concepts", type=str, metavar="DOMAIN",
                        help="Generate canonical concepts for a domain")
    parser.add_argument("--check-closure", type=str, metavar="DOMAIN",
                        help="Check closure status for a domain")
    parser.add_argument("--update-manifest", type=str, metavar="DOMAIN",
                        help="Update manifest with domain status")
    parser.add_argument("--discover", action="store_true",
                        help="Discover and add new domains to queue")
    parser.add_argument("--discover-count", type=int, default=5,
                        help="Number of domains to discover (default: 5)")
    parser.add_argument("--refill-queue", action="store_true",
                        help="Refill queue if running low (< 3 pending)")
    parser.add_argument("--auto", action="store_true",
                        help="Full auto-expansion cycle")

    args = parser.parse_args()

    if args.status:
        print_status()

    elif args.pick_next:
        domain = pick_next_domain()
        if domain:
            print(f"NEXT_DOMAIN={domain}")

    elif args.lock:
        lock_domain(args.lock)

    elif args.unlock:
        unlock_domain(args.unlock, "completed")

    elif args.generate_concepts:
        concepts = generate_concepts_for_domain(args.generate_concepts)
        if concepts:
            save_canonical_concepts(args.generate_concepts, concepts)

    elif args.check_closure:
        status = check_domain_closure(args.check_closure)
        if status:
            print(f"\nDomain: {args.check_closure}")
            print(f"Closed: {'YES' if status['closed'] else 'NO'}")
            print(f"Completion: {status['completion']}%")
            print(f"Concepts: {status['concepts']}")
            print(f"Pages: {status['pages']}")

    elif args.update_manifest:
        status = check_domain_closure(args.update_manifest)
        if status:
            update_manifest(args.update_manifest, status)

    elif args.discover:
        new_domains = discover_new_domains(count=args.discover_count)
        if new_domains:
            add_domains_to_queue(new_domains)
        else:
            print("No new domains discovered")

    elif args.refill_queue:
        check_and_refill_queue(min_pending=3, refill_count=5)

    elif args.auto:
        # Full auto-expansion cycle
        print("Starting auto-expansion cycle...")

        # 1. Pick next domain
        domain = pick_next_domain()
        if not domain:
            print("No domains to process. Exiting.")
            return

        # 2. Lock it
        lock_domain(domain)

        # 3. Check if concepts exist, generate if not
        concepts_file = BASE_DIR / f"canonical_concepts_{domain}.json"
        if not concepts_file.exists():
            print(f"Generating concepts for {domain}...")
            concepts = generate_concepts_for_domain(domain)
            if concepts:
                save_canonical_concepts(domain, concepts)
            else:
                print("Failed to generate concepts. Aborting.")
                unlock_domain(domain, "blocked")
                return

        # 4. Print instructions for knowledge_pages.py
        print(f"\n{'=' * 60}")
        print("NEXT STEP: Run page generation")
        print("=" * 60)
        print(f"python knowledge_pages.py --generate-expanded --category {domain} --count 200")
        print("=" * 60 + "\n")

    else:
        print_status()
        parser.print_help()


if __name__ == "__main__":
    main()
