"""
Educational Infographics Module
Generates educational content for:
- Teachers Pay Teachers
- Stock media (classroom posters)
- POD (educational posters)

High-demand categories for young learners.
Supports multiple languages for broader market reach.
"""

import random

# =============================================================================
# LANGUAGE SUPPORT - Expand market reach
# =============================================================================

LANGUAGES = {
    "english": {
        "code": "en",
        "label": "English",
        "keywords_suffix": [],
    },
    "spanish": {
        "code": "es",
        "label": "Spanish",
        "keywords_suffix": ["en espanol", "spanish", "bilingual"],
        "translate_prompt": "Create this infographic in Spanish language. All text labels should be in Spanish.",
    },
    "french": {
        "code": "fr",
        "label": "French",
        "keywords_suffix": ["en francais", "french"],
        "translate_prompt": "Create this infographic in French language. All text labels should be in French.",
    },
}

# =============================================================================
# LIFE CYCLES - Very popular with teachers
# =============================================================================

LIFE_CYCLES = {
    "butterfly": {
        "stages": ["egg", "caterpillar (larva)", "chrysalis (pupa)", "adult butterfly"],
        "fun_facts": [
            "Butterflies taste with their feet",
            "A group of butterflies is called a flutter",
        ],
        "colors": ["bright", "colorful", "nature greens and oranges"],
        "keywords": ["butterfly life cycle", "metamorphosis", "insect life cycle", "science poster"],
    },
    "frog": {
        "stages": ["egg (spawn)", "tadpole", "tadpole with legs", "froglet", "adult frog"],
        "fun_facts": [
            "Frogs absorb water through their skin",
            "A group of frogs is called an army",
        ],
        "colors": ["greens", "pond blues", "nature tones"],
        "keywords": ["frog life cycle", "amphibian", "pond life", "science poster"],
    },
    "chicken": {
        "stages": ["egg", "embryo", "chick hatching", "chick", "adult chicken"],
        "fun_facts": [
            "Chickens can remember over 100 faces",
            "Hens talk to their chicks while still in the egg",
        ],
        "colors": ["warm yellows", "farm colors", "rustic"],
        "keywords": ["chicken life cycle", "farm animals", "egg to chicken", "science poster"],
    },
    "fly": {
        "stages": ["egg", "larva (maggot)", "pupa", "adult fly"],
        "fun_facts": [
            "Flies can taste with their feet",
            "A fly's life cycle takes only 7-10 days",
        ],
        "colors": ["educational blues", "clean scientific"],
        "keywords": ["fly life cycle", "insect", "housefly", "science poster"],
    },
    "bee": {
        "stages": ["egg", "larva", "pupa", "adult bee"],
        "fun_facts": [
            "Bees visit 50-100 flowers in one trip",
            "Honey bees can fly up to 15 mph",
        ],
        "colors": ["yellows and blacks", "honey tones", "garden colors"],
        "keywords": ["bee life cycle", "honeybee", "pollinator", "science poster"],
    },
    "ladybug": {
        "stages": ["egg", "larva", "pupa", "adult ladybug"],
        "fun_facts": [
            "Ladybugs can eat up to 5,000 aphids in their lifetime",
            "Their bright colors warn predators they taste bad",
        ],
        "colors": ["reds and blacks", "garden greens", "bright"],
        "keywords": ["ladybug life cycle", "ladybird", "beetle", "insect poster"],
    },
    "plant": {
        "stages": ["seed", "germination", "seedling", "mature plant", "flowering", "seed production"],
        "fun_facts": [
            "Plants can communicate through their roots",
            "Some seeds can survive for hundreds of years",
        ],
        "colors": ["greens", "earth tones", "nature"],
        "keywords": ["plant life cycle", "seed to plant", "germination", "botany"],
    },
    "salmon": {
        "stages": ["egg", "alevin", "fry", "smolt", "adult salmon", "spawning"],
        "fun_facts": [
            "Salmon return to the exact stream where they were born",
            "They can jump up to 12 feet high",
        ],
        "colors": ["ocean blues", "river tones", "salmon pink"],
        "keywords": ["salmon life cycle", "fish life cycle", "migration", "science poster"],
    },
    "mosquito": {
        "stages": ["egg", "larva (wriggler)", "pupa (tumbler)", "adult mosquito"],
        "fun_facts": [
            "Only female mosquitoes bite",
            "Mosquitoes are attracted to carbon dioxide",
        ],
        "colors": ["scientific blues", "water tones", "educational"],
        "keywords": ["mosquito life cycle", "insect", "pest", "science poster"],
    },
    "turtle": {
        "stages": ["egg", "hatchling", "juvenile", "adult turtle"],
        "fun_facts": [
            "Sea turtles return to the same beach where they were born",
            "Some turtles can live over 100 years",
        ],
        "colors": ["ocean blues", "sandy tones", "greens"],
        "keywords": ["turtle life cycle", "sea turtle", "reptile", "marine life"],
    },
}

# =============================================================================
# SCIENCE DIAGRAMS
# =============================================================================

SCIENCE_DIAGRAMS = {
    "water_cycle": {
        "elements": ["evaporation", "condensation", "precipitation", "collection"],
        "style": "colorful educational diagram",
        "keywords": ["water cycle", "hydrological cycle", "evaporation", "science poster"],
    },
    "food_chain": {
        "elements": ["sun", "producer (plant)", "primary consumer", "secondary consumer", "decomposer"],
        "variations": ["forest", "ocean", "desert", "pond"],
        "keywords": ["food chain", "food web", "ecosystem", "science poster"],
    },
    "solar_system": {
        "elements": ["Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
        "style": "colorful planets in order",
        "keywords": ["solar system", "planets", "space", "astronomy poster"],
    },
    "human_body": {
        "systems": ["skeletal", "muscular", "digestive", "circulatory", "respiratory", "nervous"],
        "style": "child-friendly anatomical",
        "keywords": ["human body", "anatomy", "body systems", "science poster"],
    },
    "rock_cycle": {
        "elements": ["igneous rock", "sedimentary rock", "metamorphic rock", "magma"],
        "processes": ["weathering", "erosion", "heat and pressure", "melting", "cooling"],
        "keywords": ["rock cycle", "geology", "rocks and minerals", "earth science"],
    },
    "states_of_matter": {
        "states": ["solid", "liquid", "gas"],
        "examples": ["ice", "water", "steam"],
        "keywords": ["states of matter", "solid liquid gas", "chemistry", "science poster"],
    },
    "photosynthesis": {
        "elements": ["sunlight", "carbon dioxide", "water", "glucose", "oxygen"],
        "style": "plant diagram with arrows",
        "keywords": ["photosynthesis", "plant science", "biology", "science poster"],
    },
    "weather": {
        "types": ["sunny", "cloudy", "rainy", "snowy", "windy", "stormy"],
        "style": "cute weather icons chart",
        "keywords": ["weather chart", "weather types", "meteorology", "classroom poster"],
    },
}

# =============================================================================
# MATH VISUALS
# =============================================================================

MATH_VISUALS = {
    "times_tables": {
        "tables": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "style": "colorful grid with visual aids",
        "keywords": ["times table", "multiplication chart", "math poster", "classroom"],
    },
    "shapes_2d": {
        "shapes": ["circle", "square", "triangle", "rectangle", "pentagon", "hexagon", "octagon", "oval"],
        "style": "colorful shape chart with labels",
        "keywords": ["2D shapes", "geometry", "shapes poster", "math poster"],
    },
    "shapes_3d": {
        "shapes": ["sphere", "cube", "cylinder", "cone", "pyramid", "prism"],
        "style": "3D shapes with labels",
        "keywords": ["3D shapes", "geometry", "solid shapes", "math poster"],
    },
    "fractions": {
        "fractions": ["1/2", "1/3", "1/4", "2/3", "3/4"],
        "style": "pie charts and visual fraction bars",
        "keywords": ["fractions", "fraction chart", "math visual", "math poster"],
    },
    "number_line": {
        "range": "0-20 or 0-100",
        "style": "colorful number line with marks",
        "keywords": ["number line", "counting", "math poster", "classroom"],
    },
    "place_value": {
        "elements": ["ones", "tens", "hundreds", "thousands"],
        "style": "blocks and visual representation",
        "keywords": ["place value", "number sense", "math poster", "classroom"],
    },
    "telling_time": {
        "elements": ["clock face", "hour hand", "minute hand", "digital time"],
        "style": "colorful clock with examples",
        "keywords": ["telling time", "clock", "time poster", "math poster"],
    },
    "money": {
        "elements": ["penny", "nickel", "dime", "quarter", "dollar"],
        "style": "coin chart with values",
        "keywords": ["money chart", "coins", "currency", "math poster"],
    },
}

# =============================================================================
# LANGUAGE & LITERACY
# =============================================================================

LANGUAGE_VISUALS = {
    "alphabet": {
        "style": "A-Z with pictures for each letter",
        "variations": ["animals", "objects", "food"],
        "keywords": ["alphabet chart", "ABC poster", "phonics", "classroom"],
    },
    "vowels_consonants": {
        "vowels": ["A", "E", "I", "O", "U"],
        "style": "colorful chart distinguishing vowels and consonants",
        "keywords": ["vowels", "consonants", "phonics", "language arts"],
    },
    "parts_of_speech": {
        "parts": ["noun", "verb", "adjective", "adverb", "pronoun", "preposition"],
        "style": "colorful examples for each",
        "keywords": ["parts of speech", "grammar", "language arts", "classroom poster"],
    },
    "punctuation": {
        "marks": ["period", "comma", "question mark", "exclamation point", "quotation marks"],
        "style": "examples showing usage",
        "keywords": ["punctuation", "grammar", "writing", "classroom poster"],
    },
    "sight_words": {
        "words": "common sight words for grade level",
        "style": "colorful word wall style",
        "keywords": ["sight words", "high frequency words", "reading", "phonics"],
    },
    "color_words": {
        "colors": ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black", "white"],
        "style": "color swatches with word labels",
        "keywords": ["color words", "colors chart", "preschool", "classroom"],
    },
    "number_words": {
        "numbers": "one through twenty",
        "style": "number with word and visual quantity",
        "keywords": ["number words", "counting", "preschool", "classroom"],
    },
}

# =============================================================================
# SOCIAL STUDIES
# =============================================================================

SOCIAL_STUDIES = {
    "continents": {
        "elements": ["Africa", "Antarctica", "Asia", "Australia", "Europe", "North America", "South America"],
        "style": "world map with labeled continents",
        "keywords": ["continents", "world map", "geography", "social studies"],
    },
    "community_helpers": {
        "helpers": ["doctor", "firefighter", "police officer", "teacher", "nurse", "mail carrier"],
        "style": "cute illustrations with labels",
        "keywords": ["community helpers", "careers", "social studies", "preschool"],
    },
    "seasons": {
        "seasons": ["spring", "summer", "fall", "winter"],
        "elements": "weather, activities, clothing for each",
        "keywords": ["seasons", "four seasons", "weather", "classroom poster"],
    },
    "days_of_week": {
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "style": "colorful calendar style",
        "keywords": ["days of the week", "calendar", "classroom poster", "preschool"],
    },
    "months_of_year": {
        "months": "January through December",
        "style": "seasonal illustrations for each month",
        "keywords": ["months of the year", "calendar", "classroom poster", "seasons"],
    },
}


def generate_educational_ideas(count=5, languages=None):
    """
    Generate educational infographic design ideas.

    Args:
        count: Number of ideas to generate
        languages: List of languages to generate for (default: english + spanish)

    Returns list of design ideas optimized for educational content.
    """
    if languages is None:
        languages = ["english", "spanish"]  # Default: create both versions

    ideas = []

    # Life Cycles (most popular)
    life_cycle_keys = list(LIFE_CYCLES.keys())
    random.shuffle(life_cycle_keys)

    for key in life_cycle_keys[:3]:
        cycle = LIFE_CYCLES[key]
        stages_text = " -> ".join(cycle["stages"])

        # Generate for each language
        for lang in languages:
            lang_info = LANGUAGES.get(lang, LANGUAGES["english"])
            lang_suffix = f" ({lang_info['label']})" if lang != "english" else ""
            translate_instruction = lang_info.get("translate_prompt", "")

            idea = {
                "type": "educational",
                "category": "life_cycle",
                "subject": key,
                "template": "infographic",
                "priority": "high",
                "language": lang,
                "prompt_vars": {
                    "title": f"Life Cycle of a {key.title()}{lang_suffix}",
                    "content": f"Educational diagram showing: {stages_text}. {translate_instruction}",
                    "style": "child-friendly, colorful, educational poster style",
                    "color_scheme": random.choice(cycle["colors"]),
                },
                "tags": cycle["keywords"] + lang_info.get("keywords_suffix", []) + ["educational", "classroom"],
                "platforms": ["wirestock", "redbubble", "teachers_pay_teachers"],
            }
            ideas.append(idea)

    # Science Diagrams
    science_keys = list(SCIENCE_DIAGRAMS.keys())
    random.shuffle(science_keys)

    for key in science_keys[:2]:
        diagram = SCIENCE_DIAGRAMS[key]

        if "elements" in diagram:
            content = ", ".join(diagram["elements"])
        elif "systems" in diagram:
            content = random.choice(diagram["systems"]) + " system"
        else:
            content = key.replace("_", " ")

        idea = {
            "type": "educational",
            "category": "science",
            "subject": key,
            "template": "infographic",
            "priority": "high",
            "prompt_vars": {
                "title": key.replace("_", " ").title(),
                "content": f"Educational diagram showing {content}",
                "style": diagram.get("style", "colorful educational diagram"),
                "color_scheme": "bright educational colors",
            },
            "tags": diagram["keywords"] + ["educational", "science", "classroom"],
            "platforms": ["wirestock", "redbubble"],
        }
        ideas.append(idea)

    # Math Visuals
    math_keys = list(MATH_VISUALS.keys())
    random.shuffle(math_keys)

    for key in math_keys[:2]:
        visual = MATH_VISUALS[key]

        if key == "times_tables":
            table_num = random.choice(visual["tables"])
            title = f"{table_num} Times Table"
            content = f"Multiplication table for {table_num}"
        else:
            title = key.replace("_", " ").title()
            content = key.replace("_", " ")

        idea = {
            "type": "educational",
            "category": "math",
            "subject": key,
            "template": "infographic",
            "priority": "medium",
            "prompt_vars": {
                "title": title,
                "content": f"Educational chart showing {content}",
                "style": visual.get("style", "colorful math chart"),
                "color_scheme": "bright primary colors",
            },
            "tags": visual["keywords"] + ["educational", "math", "classroom"],
            "platforms": ["wirestock", "redbubble"],
        }
        ideas.append(idea)

    # Language/Literacy
    lang_keys = list(LANGUAGE_VISUALS.keys())
    random.shuffle(lang_keys)

    for key in lang_keys[:1]:
        visual = LANGUAGE_VISUALS[key]

        idea = {
            "type": "educational",
            "category": "language",
            "subject": key,
            "template": "infographic",
            "priority": "medium",
            "prompt_vars": {
                "title": key.replace("_", " ").title(),
                "content": f"Educational chart for {key.replace('_', ' ')}",
                "style": visual.get("style", "colorful classroom chart"),
                "color_scheme": "rainbow colors",
            },
            "tags": visual["keywords"] + ["educational", "literacy", "classroom"],
            "platforms": ["wirestock", "redbubble"],
        }
        ideas.append(idea)

    # Social Studies
    social_keys = list(SOCIAL_STUDIES.keys())
    random.shuffle(social_keys)

    for key in social_keys[:1]:
        topic = SOCIAL_STUDIES[key]

        idea = {
            "type": "educational",
            "category": "social_studies",
            "subject": key,
            "template": "infographic",
            "priority": "medium",
            "prompt_vars": {
                "title": key.replace("_", " ").title(),
                "content": f"Educational poster about {key.replace('_', ' ')}",
                "style": topic.get("style", "colorful educational poster"),
                "color_scheme": "friendly bright colors",
            },
            "tags": topic["keywords"] + ["educational", "social studies", "classroom"],
            "platforms": ["wirestock", "redbubble"],
        }
        ideas.append(idea)

    random.shuffle(ideas)
    return ideas[:count]


# Infographic-specific prompt template
INFOGRAPHIC_TEMPLATE = {
    "prompt_template": "Educational infographic poster: {title}. {content}. Style: {style}, {color_scheme} color palette. Child-friendly, clear labels, professional educational design, suitable for classroom printing, high resolution",
    "product_types": ["poster", "digital download", "printable"],
}


if __name__ == "__main__":
    print("=" * 60)
    print("EDUCATIONAL CONTENT TEST")
    print("=" * 60)

    ideas = generate_educational_ideas(count=10)

    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. [{idea['category'].upper()}] {idea['prompt_vars']['title']}")
        print(f"   Tags: {', '.join(idea['tags'][:4])}")
