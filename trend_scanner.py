"""
Trend Scanner
Automatically finds trending topics for design generation.

Sources:
- Google Trends (pytrends)
- Etsy trending searches
- Pinterest trends
- Seasonal calendar
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("Warning: pytrends not installed. Run: pip install pytrends")

from config import NICHES, SEASONAL_CALENDAR, DESIGN_TEMPLATES
from micro_niches import (
    DOG_BREEDS, CAT_BREEDS, PROFESSIONS, HOBBIES, IDENTITIES,
    get_dog_breed_designs, get_profession_designs, get_hobby_designs
)
from educational_content import generate_educational_ideas, INFOGRAPHIC_TEMPLATE

# Paths
BASE_DIR = Path(__file__).parent
TRENDS_CACHE = BASE_DIR / "trends_cache.json"
USED_IDEAS = BASE_DIR / "used_ideas.json"


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "[i]", "SUCCESS": "[+]", "ERROR": "[!]", "WARN": "[*]"}.get(level, "")
    print(f"[{timestamp}] {prefix} {message}")


def load_used_ideas():
    """Load previously used design ideas to avoid duplicates."""
    if USED_IDEAS.exists():
        return set(json.loads(USED_IDEAS.read_text()))
    return set()


def save_used_idea(idea_hash):
    """Save a used idea hash."""
    used = load_used_ideas()
    used.add(idea_hash)
    # Keep only last 10,000 ideas
    if len(used) > 10000:
        used = set(list(used)[-10000:])
    USED_IDEAS.write_text(json.dumps(list(used)))


def get_google_trends(keywords, timeframe='today 3-m'):
    """Fetch related queries from Google Trends."""
    if not PYTRENDS_AVAILABLE:
        return []

    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        trends = []

        for keyword in keywords[:5]:  # Limit to avoid rate limits
            pytrends.build_payload([keyword], cat=0, timeframe=timeframe)
            related = pytrends.related_queries()

            if keyword in related and related[keyword]['rising'] is not None:
                rising = related[keyword]['rising']
                for _, row in rising.head(10).iterrows():
                    trends.append({
                        'query': row['query'],
                        'value': row['value'],
                        'source': 'google_trends',
                        'parent_keyword': keyword
                    })

        log(f"Found {len(trends)} trending queries from Google Trends", "SUCCESS")
        return trends

    except Exception as e:
        log(f"Google Trends error: {e}", "WARN")
        return []


def get_seasonal_trends():
    """Get upcoming seasonal events that need designs."""
    today = datetime.now()
    trends = []

    for date_str, event_info in SEASONAL_CALENDAR.items():
        # Parse date (assume current year, or next year if passed)
        month, day = map(int, date_str.split('-'))
        event_date = datetime(today.year, month, day)

        if event_date < today:
            event_date = datetime(today.year + 1, month, day)

        days_until = (event_date - today).days
        lead_time = event_info['days_before']

        # Check if we should start creating designs for this event
        if days_until <= lead_time and days_until > 0:
            trends.append({
                'event': event_info['event'],
                'days_until': days_until,
                'priority': lead_time - days_until,  # Higher = more urgent
                'designs_needed': event_info['designs'],
                'source': 'seasonal'
            })

    # Sort by priority (most urgent first)
    trends.sort(key=lambda x: x['priority'], reverse=True)

    if trends:
        log(f"Found {len(trends)} upcoming seasonal events", "SUCCESS")

    return trends


def get_niche_keywords():
    """Generate keyword combinations from configured niches."""
    keywords = []

    for niche_name, niche_config in NICHES.items():
        if not niche_config.get('enabled', True):
            continue

        for sub_niche in niche_config.get('sub_niches', []):
            for style in niche_config.get('styles', ['modern']):
                keywords.append({
                    'niche': niche_name,
                    'sub_niche': sub_niche,
                    'style': style,
                    'keywords': niche_config.get('keywords', []),
                    'source': 'niche_config'
                })

    return keywords


def generate_design_ideas(count=10):
    """
    Generate MICRO-NICHE design ideas that actually sell:
    - Specific dog/cat breeds with identity (Mom/Dad)
    - Profession specialties with inside jokes
    - Hobby types with specific angles
    - Seasonal events
    """
    ideas = []
    used = load_used_ideas()

    # Get seasonal events (high priority)
    seasonal = get_seasonal_trends()

    # =================================================================
    # MICRO-NICHE IDEAS (These are what actually sell!)
    # =================================================================

    # 1. DOG BREEDS - Specific breeds with real jokes
    dog_breed_keys = list(DOG_BREEDS.keys())
    random.shuffle(dog_breed_keys)

    for breed_key in dog_breed_keys[:8]:
        breed = DOG_BREEDS[breed_key]
        breed_name = breed['names'][0]
        identity = random.choice(['Mom', 'Dad', 'Parent', 'Owner'])
        joke = random.choice(breed.get('jokes', [f"I love my {breed_name}"]))

        idea = {
            'type': 'micro_niche',
            'category': 'dog_breed',
            'niche': 'dogs',
            'sub_niche': breed_name,
            'breed_key': breed_key,
            'identity': identity,
            'template': 'typography',
            'priority': 'high',
            'prompt_vars': {
                'quote': joke,
                'subject': breed_name,
                'style': random.choice(['bold modern', 'hand-lettered', 'vintage']),
                'color_scheme': random.choice(['vibrant', 'earth tones', 'black and white']),
            },
            'tags': [breed_name.lower(), f'{breed_name.lower()} {identity.lower()}',
                    'dog lover', 'dog gift', breed_key.replace('_', ' ')],
        }

        idea_hash = f"dog_{breed_key}_{joke[:30]}_{identity}"
        if idea_hash not in used:
            ideas.append(idea)

    # 2. CAT BREEDS
    cat_breed_keys = list(CAT_BREEDS.keys())
    random.shuffle(cat_breed_keys)

    for breed_key in cat_breed_keys[:4]:
        breed = CAT_BREEDS[breed_key]
        breed_name = breed['names'][0]
        identity = random.choice(['Mom', 'Dad', 'Parent'])
        joke = random.choice(breed.get('jokes', [f"I love my {breed_name}"]))

        idea = {
            'type': 'micro_niche',
            'category': 'cat_breed',
            'niche': 'cats',
            'sub_niche': breed_name,
            'breed_key': breed_key,
            'identity': identity,
            'template': 'typography',
            'priority': 'high',
            'prompt_vars': {
                'quote': joke,
                'subject': breed_name,
                'style': random.choice(['bold modern', 'playful', 'minimalist']),
                'color_scheme': random.choice(['vibrant', 'pastel', 'black and white']),
            },
            'tags': [breed_name.lower(), f'{breed_name.lower()} {identity.lower()}',
                    'cat lover', 'cat gift', 'crazy cat lady'],
        }

        idea_hash = f"cat_{breed_key}_{joke[:30]}_{identity}"
        if idea_hash not in used:
            ideas.append(idea)

    # 3. PROFESSIONS - Specific specialties
    profession_keys = list(PROFESSIONS.keys())
    random.shuffle(profession_keys)

    for profession_key in profession_keys[:6]:
        profession = PROFESSIONS[profession_key]
        specialty = random.choice(profession.get('specialties', ['']))
        joke_template = random.choice(profession.get('jokes', ['{specialty} professional']))
        joke = joke_template.format(specialty=specialty) if '{specialty}' in joke_template else joke_template

        idea = {
            'type': 'micro_niche',
            'category': 'profession',
            'niche': 'professions',
            'sub_niche': profession_key,
            'specialty': specialty,
            'template': 'typography',
            'priority': 'high',
            'prompt_vars': {
                'quote': joke,
                'subject': f"{specialty} {profession_key}",
                'style': random.choice(['bold', 'distressed', 'clean modern']),
                'color_scheme': random.choice(['vibrant', 'professional', 'bold colors']),
            },
            'tags': [profession_key, specialty.lower(), 'career gift',
                    f'{profession_key} life', 'work humor', 'coworker gift'],
        }

        idea_hash = f"prof_{profession_key}_{specialty}_{joke[:30]}"
        if idea_hash not in used:
            ideas.append(idea)

    # 4. HOBBIES - Specific types
    hobby_keys = list(HOBBIES.keys())
    random.shuffle(hobby_keys)

    for hobby_key in hobby_keys[:5]:
        hobby = HOBBIES[hobby_key]
        hobby_type = random.choice(hobby.get('types', ['']))
        identity = random.choice(['Dad', 'Mom', 'Enthusiast', 'Lover'])
        joke_template = random.choice(hobby.get('jokes', ['{type} life']))
        joke = joke_template.format(type=hobby_type) if '{type}' in joke_template else joke_template

        idea = {
            'type': 'micro_niche',
            'category': 'hobby',
            'niche': 'hobbies',
            'sub_niche': hobby_key,
            'hobby_type': hobby_type,
            'identity': identity,
            'template': 'typography',
            'priority': 'medium',
            'prompt_vars': {
                'quote': joke,
                'subject': f"{hobby_type} {hobby_key}",
                'style': random.choice(['vintage', 'bold', 'rustic']),
                'color_scheme': random.choice(['earth tones', 'vintage', 'bold']),
            },
            'tags': [hobby_key, hobby_type.lower(), f'{hobby_key} {identity.lower()}',
                    'hobby gift', f'{hobby_key} lover'],
        }

        idea_hash = f"hobby_{hobby_key}_{hobby_type}_{joke[:30]}"
        if idea_hash not in used:
            ideas.append(idea)

    # 5. SEASONAL (if urgent)
    for event in seasonal[:2]:
        # Combine seasonal with micro-niche
        breed_key = random.choice(list(DOG_BREEDS.keys()))
        breed_name = DOG_BREEDS[breed_key]['names'][0]

        idea = {
            'type': 'seasonal_micro',
            'category': 'seasonal',
            'event': event['event'],
            'niche': 'dogs',
            'sub_niche': breed_name,
            'template': 'typography',
            'priority': 'high',
            'prompt_vars': {
                'quote': f"{event['event']} is better with my {breed_name}",
                'subject': f"{breed_name} {event['event']}",
                'style': 'festive bold',
                'color_scheme': 'holiday colors',
            },
            'tags': [event['event'].lower(), breed_name.lower(),
                    f"{event['event'].lower()} {breed_name.lower()}", 'holiday gift'],
        }

        idea_hash = f"seasonal_{event['event']}_{breed_name}"
        if idea_hash not in used:
            ideas.append(idea)

    # =================================================================
    # EDUCATIONAL INFOGRAPHICS (High value!)
    # =================================================================
    educational_ideas = generate_educational_ideas(count=4)
    ideas.extend(educational_ideas)

    # Shuffle and limit
    random.shuffle(ideas)
    selected = ideas[:count]

    # Mark as used
    for idea in selected:
        idea_hash = json.dumps(idea, sort_keys=True)[:100]
        save_used_idea(idea_hash)

    log(f"Generated {len(selected)} MICRO-NICHE design ideas", "SUCCESS")
    return selected


def get_quote_ideas(niche, sub_niche, count=5):
    """Generate quote ideas for typography designs."""
    quotes = {
        "pets": {
            "dogs": [
                "Life is better with a dog",
                "My dog is my therapist",
                "Home is where my dog is",
                "Dogs before dudes",
                "In dog years, I'm dead",
            ],
            "cats": [
                "Cats rule, dogs drool",
                "Home is where my cat is",
                "I was normal 3 cats ago",
                "Cat mom life",
                "I work hard so my cat can have a better life",
            ],
        },
        "professions": {
            "nurse": [
                "Nurse life",
                "Too cute to be a doctor",
                "Nurses call the shots",
                "Saving lives is my cardio",
                "I'm a nurse, what's your superpower?",
            ],
            "teacher": [
                "Teaching is a work of heart",
                "Teach love inspire",
                "Best teacher ever",
                "I teach tiny humans",
                "Teachers change the world",
            ],
            "developer": [
                "I turn coffee into code",
                "Eat sleep code repeat",
                "There's no place like 127.0.0.1",
                "It works on my machine",
                "// TODO: write better code",
            ],
        },
        "hobbies": {
            "fishing": [
                "Reel cool dad",
                "Born to fish, forced to work",
                "I'd rather be fishing",
                "Hooked on fishing",
                "Fish fear me",
            ],
            "gaming": [
                "Eat sleep game repeat",
                "Level up",
                "Game over? Never.",
                "I paused my game to be here",
                "Gamer dad",
            ],
        },
        "motivation": {
            "success": [
                "Hustle until your haters ask if you're hiring",
                "Good things take time",
                "Make it happen",
                "Stay hungry, stay foolish",
                "Dream big, work hard",
            ],
            "fitness": [
                "No pain no gain",
                "Stronger than yesterday",
                "Gym hair don't care",
                "Sweat is fat crying",
                "Train insane or remain the same",
            ],
        },
    }

    # Get quotes for the niche/sub_niche
    niche_quotes = quotes.get(niche, {}).get(sub_niche, [])

    if not niche_quotes:
        # Generic fallback
        niche_quotes = [
            f"I love {sub_niche}",
            f"{sub_niche.title()} life",
            f"Best {sub_niche} ever",
            f"Living my best {sub_niche} life",
            f"All about {sub_niche}",
        ]

    return random.sample(niche_quotes, min(count, len(niche_quotes)))


if __name__ == "__main__":
    # Test the trend scanner
    print("=" * 60)
    print("TREND SCANNER TEST")
    print("=" * 60)

    ideas = generate_design_ideas(count=10)

    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. {idea['type'].upper()} - {idea['template']}")
        print(f"   Priority: {idea['priority']}")
        print(f"   Vars: {idea.get('prompt_vars', {})}")
