"""
MICRO-NICHE DATABASE
Specific, underserved niches that actually sell on POD.

Strategy: [Specific Subject] + [Identity] + [Humor/Pride]
Example: "Bernese Mountain Dog" + "Dad" + "My retirement plan is my dog"
"""

# =============================================================================
# DOG BREEDS - 50 most popular + niche favorites
# =============================================================================
DOG_BREEDS = {
    # High-demand breeds (passionate owners)
    "golden_retriever": {
        "names": ["Golden Retriever", "Golden"],
        "traits": ["goofy", "loyal", "fluffy", "food-obsessed"],
        "jokes": [
            "My Golden Retriever is my retirement plan",
            "I work hard so my Golden can have a better life",
            "Golden Retriever hair is my favorite accessory",
            "Sorry I'm late, my Golden needed one more belly rub",
            "I just want to be the person my Golden thinks I am",
            "Easily distracted by Golden Retrievers",
            "My therapist has four legs and a waggy tail",
        ]
    },
    "german_shepherd": {
        "names": ["German Shepherd", "GSD"],
        "traits": ["protective", "loyal", "intelligent", "alert"],
        "jokes": [
            "German Shepherd: The only alarm system that loves you back",
            "I'm not single, I have a German Shepherd",
            "My GSD thinks I'm kind of a big deal",
            "Fur, drool, and unconditional love - GSD life",
            "Warning: German Shepherd thinks they're a lap dog",
        ]
    },
    "french_bulldog": {
        "names": ["French Bulldog", "Frenchie"],
        "traits": ["snorty", "stubborn", "cuddly", "dramatic"],
        "jokes": [
            "Frenchie snores louder than my husband",
            "My Frenchie is my favorite coworker",
            "I didn't choose the Frenchie life, it chose me",
            "Powered by coffee and Frenchie cuddles",
            "My Frenchie is judging you",
        ]
    },
    "labrador": {
        "names": ["Labrador", "Lab", "Labrador Retriever"],
        "traits": ["food-obsessed", "energetic", "loyal", "derpy"],
        "jokes": [
            "Lab hair, don't care",
            "My Lab ate my excuse",
            "Labrador retriever: Will work for treats",
            "I'm just here for the Labs",
            "My Labrador is the reason I can't have nice things",
        ]
    },
    "dachshund": {
        "names": ["Dachshund", "Wiener Dog", "Doxie", "Sausage Dog"],
        "traits": ["stubborn", "brave", "long", "loud"],
        "jokes": [
            "Dachshund: Big attitude, little legs",
            "I like long walks and wiener dogs",
            "My Dachshund runs this house",
            "Life is too short for just one Dachshund",
            "Wiener dog mom/dad",
            "Long dog, short patience",
        ]
    },
    "corgi": {
        "names": ["Corgi", "Pembroke Welsh Corgi"],
        "traits": ["fluffy butt", "stubborn", "herding", "loaf"],
        "jokes": [
            "Corgi butt, don't care",
            "I work hard so my Corgi can live their best loaf life",
            "Corgi: 50% fluff, 50% attitude",
            "My Corgi herds my family",
            "Low rider, high maintenance",
            "Powered by coffee and Corgi sploot",
        ]
    },
    "husky": {
        "names": ["Husky", "Siberian Husky"],
        "traits": ["dramatic", "talkative", "escape artist", "shedding"],
        "jokes": [
            "Husky: Fur everywhere is a lifestyle",
            "My Husky is more dramatic than me",
            "Husky owner: Professional fur remover",
            "Warning: Husky will scream about everything",
            "I didn't adopt a Husky, I adopted a tornado",
        ]
    },
    "poodle": {
        "names": ["Poodle", "Standard Poodle", "Toy Poodle"],
        "traits": ["smart", "fancy", "athletic", "hypoallergenic"],
        "jokes": [
            "Poodle: Fancy on the outside, weirdo on the inside",
            "My Poodle is smarter than your honor student",
            "Poodle parent and proud",
            "Not spoiled, just well-loved Poodle",
        ]
    },
    "beagle": {
        "names": ["Beagle"],
        "traits": ["nose-driven", "howling", "food-obsessed", "stubborn"],
        "jokes": [
            "Beagle: Will sniff everything",
            "My Beagle's nose runs the show",
            "Beagle parent: Professional treat dispenser",
            "If my Beagle doesn't like you, I don't like you",
        ]
    },
    "pitbull": {
        "names": ["Pitbull", "Pit Bull", "Pittie", "Pibble"],
        "traits": ["cuddly", "misunderstood", "velcro dog", "smile"],
        "jokes": [
            "Pitbull: 100% cuddle monster",
            "My Pittie thinks they're a lap dog",
            "Advocate for pitties and proud",
            "Pitbulls: Changing hearts one wiggle at a time",
            "I'm a Pitbull person, deal with it",
        ]
    },
    "rottweiler": {
        "names": ["Rottweiler", "Rottie"],
        "traits": ["loyal", "protective", "gentle giant", "leaner"],
        "jokes": [
            "Rottweiler: The best leaning post",
            "My Rottie thinks they're a lap dog",
            "Rottweiler parent: Big dog, bigger heart",
            "Warning: Rottweiler will lean on you with love",
        ]
    },
    "australian_shepherd": {
        "names": ["Australian Shepherd", "Aussie"],
        "traits": ["energetic", "herding", "smart", "wiggle butt"],
        "jokes": [
            "Aussie: More energy than a toddler on espresso",
            "My Australian Shepherd runs my schedule",
            "Powered by Aussie zoomies",
            "Australian Shepherd owner: Professional ball thrower",
        ]
    },
    "shiba_inu": {
        "names": ["Shiba Inu", "Shiba"],
        "traits": ["dramatic", "cat-like", "screaming", "independent"],
        "jokes": [
            "Shiba Inu: Much drama, very attitude",
            "My Shiba screams at everything",
            "Shiba Inu: Dog hardware, cat software",
            "Living with a Shiba is never boring",
        ]
    },
    "bernese_mountain_dog": {
        "names": ["Bernese Mountain Dog", "Berner", "BMD"],
        "traits": ["gentle giant", "fluffy", "cuddly", "drooly"],
        "jokes": [
            "Bernese Mountain Dog: 100 pounds of love",
            "I work hard so my Berner can nap in comfort",
            "My Bernese thinks they're a lap dog",
            "Berner floof is my favorite accessory",
        ]
    },
    "boxer": {
        "names": ["Boxer"],
        "traits": ["goofy", "wiggly", "bouncy", "loyal"],
        "jokes": [
            "Boxer: 60 pounds of wiggle",
            "My Boxer has two speeds: zoom and sleep",
            "Boxer owner: Professional wiggle handler",
            "Warning: Boxer will bounce on you",
        ]
    },
    "great_dane": {
        "names": ["Great Dane", "Dane"],
        "traits": ["gentle giant", "couch hog", "tall", "goofy"],
        "jokes": [
            "Great Dane: Horse disguised as a dog",
            "My Great Dane IS the couch",
            "I need a bigger couch - Great Dane parent",
            "Great Dane: Lap dog in their mind",
        ]
    },
    "border_collie": {
        "names": ["Border Collie"],
        "traits": ["smart", "intense", "herding", "workaholic"],
        "jokes": [
            "Border Collie: Smarter than me since day one",
            "My Border Collie has a job and I'm the assistant",
            "Warning: Border Collie will herd you",
            "Powered by Border Collie chaos",
        ]
    },
    "chihuahua": {
        "names": ["Chihuahua", "Chi"],
        "traits": ["tiny but mighty", "sassy", "shivering", "fierce"],
        "jokes": [
            "Chihuahua: 5 pounds of pure attitude",
            "My Chihuahua runs this house",
            "Tiny dog, huge personality - Chihuahua life",
            "Chihuahua: Will fight anyone, anytime",
        ]
    },
    "maltese": {
        "names": ["Maltese"],
        "traits": ["fluffy", "tiny", "sassy", "lap dog"],
        "jokes": [
            "Maltese: Fluff with attitude",
            "My Maltese is the real boss",
            "Maltese parent: Professional fluff maintenance",
        ]
    },
    "pomeranian": {
        "names": ["Pomeranian", "Pom"],
        "traits": ["fluffy", "sassy", "yappy", "confident"],
        "jokes": [
            "Pomeranian: Big personality, tiny body",
            "My Pom thinks they're a Great Dane",
            "Pomeranian: Fluff, sass, and attitude",
        ]
    },
}

# =============================================================================
# CAT BREEDS - For the cat people
# =============================================================================
CAT_BREEDS = {
    "orange_cat": {
        "names": ["Orange Cat", "Orange Tabby", "Ginger Cat"],
        "traits": ["one brain cell", "chaotic", "loveable idiot"],
        "jokes": [
            "Orange cat: One brain cell, unlimited chaos",
            "My orange cat shares the brain cell today",
            "Orange cats: Chaos wrapped in fur",
            "Proud parent of an orange idiot",
        ]
    },
    "black_cat": {
        "names": ["Black Cat", "Void", "House Panther"],
        "traits": ["void", "spooky", "misunderstood", "lucky"],
        "jokes": [
            "Black cat: My personal house panther",
            "The void stares back and wants treats",
            "Black cats are good luck, fight me",
            "My black cat is not bad luck, you are",
        ]
    },
    "maine_coon": {
        "names": ["Maine Coon"],
        "traits": ["giant", "fluffy", "dog-like", "majestic"],
        "jokes": [
            "Maine Coon: That's not a cat, that's a lynx",
            "My Maine Coon is bigger than most dogs",
            "Maine Coon parent: Professional fur remover",
        ]
    },
    "siamese": {
        "names": ["Siamese", "Siamese Cat"],
        "traits": ["vocal", "demanding", "clingy", "dramatic"],
        "jokes": [
            "Siamese: Will yell at you about everything",
            "My Siamese has an opinion and will share it",
            "Siamese cat: The most dramatic roommate",
        ]
    },
    "ragdoll": {
        "names": ["Ragdoll", "Ragdoll Cat"],
        "traits": ["floppy", "cuddly", "blue eyes", "chill"],
        "jokes": [
            "Ragdoll: Professional flopper",
            "My Ragdoll goes limp for cuddles",
            "Ragdoll cat: Born to flop",
        ]
    },
    "bengal": {
        "names": ["Bengal", "Bengal Cat"],
        "traits": ["wild", "athletic", "chatty", "trouble"],
        "jokes": [
            "Bengal cat: Part cat, part chaos",
            "My Bengal thinks they're a leopard",
            "Bengal parent: Never a dull moment",
        ]
    },
    "tuxedo_cat": {
        "names": ["Tuxedo Cat", "Tuxie"],
        "traits": ["fancy", "mischievous", "distinguished"],
        "jokes": [
            "Tuxedo cat: Always dressed for the occasion",
            "My cat wears a tuxedo better than I do",
            "Tuxedo cat: Formal attire, feral behavior",
        ]
    },
    "tabby": {
        "names": ["Tabby", "Tabby Cat"],
        "traits": ["classic", "striped", "sweet"],
        "jokes": [
            "Tabby cat: Classic stripes, classic attitude",
            "Proud tabby parent",
        ]
    },
}

# =============================================================================
# PROFESSIONS - Inside jokes that only THEY understand
# =============================================================================
PROFESSIONS = {
    "nurse": {
        "specialties": ["ICU", "ER", "NICU", "OR", "Night Shift", "Psych", "Peds", "L&D"],
        "jokes": [
            "{specialty} Nurse: Powered by coffee and inappropriate humor",
            "{specialty} Nurse: I've seen things you wouldn't believe",
            "Night Shift {specialty}: Vampire hours, nurse pay",
            "{specialty} Nurse: Not all heroes wear capes, some wear scrubs",
            "Warning: {specialty} Nurse with low patience",
            "{specialty} Nurse: Fluent in medical and sarcasm",
            "Yes I'm a {specialty} nurse. No, I can't diagnose your rash",
        ]
    },
    "teacher": {
        "specialties": ["Kindergarten", "Elementary", "Middle School", "High School", "Math", "Science", "English", "Art", "Music", "PE", "Special Ed", "ESL"],
        "jokes": [
            "{specialty} Teacher: Fueled by coffee and student excuses",
            "{specialty} Teacher: I have eyes in the back of my head",
            "{specialty} Teacher: My patience is tested daily",
            "{specialty} Teacher: Making a difference, questioning my choices",
            "I'm a {specialty} Teacher - I can't fix stupid but I can educate it",
            "{specialty} Teacher: Overworked, underpaid, wouldn't trade it",
        ]
    },
    "developer": {
        "specialties": ["Frontend", "Backend", "Full Stack", "DevOps", "Python", "JavaScript", "Java", "React", "Data"],
        "jokes": [
            "{specialty} Developer: I turn caffeine into code",
            "{specialty} Developer: It works on my machine",
            "{specialty}: 99 bugs in the code, 99 bugs... fix one, 127 bugs",
            "{specialty} Developer: Googling errors since day one",
            "{specialty}: My code doesn't have bugs, it has features",
            "{specialty} Dev: I don't always test my code, but when I do, I do it in production",
            "// TODO: {specialty} life",
        ]
    },
    "accountant": {
        "specialties": ["CPA", "Tax", "Auditor", "Forensic", "Corporate"],
        "jokes": [
            "{specialty} Accountant: I'm here to audit your life choices",
            "{specialty}: My favorite time of year is after April 15th",
            "{specialty} Accountant: I make numbers behave",
            "{specialty}: Balance sheets by day, wine by night",
            "{specialty} Accountant: Keeping it balanced since graduation",
        ]
    },
    "electrician": {
        "specialties": ["Journeyman", "Master", "Commercial", "Residential", "Industrial"],
        "jokes": [
            "{specialty} Electrician: I have potential",
            "{specialty} Electrician: Currently awesome",
            "{specialty} Electrician: We're the ones who make things light up",
            "{specialty} Electrician: Shocking personality",
            "{specialty} Electrician: I work with high voltage so you don't have to",
        ]
    },
    "plumber": {
        "specialties": ["Master", "Journeyman", "Commercial", "Residential"],
        "jokes": [
            "{specialty} Plumber: I deal with your crap so you don't have to",
            "{specialty} Plumber: A good flush beats a full house",
            "{specialty} Plumber: We're #1 in the #2 business",
            "{specialty} Plumber: Pipe dreams are my reality",
        ]
    },
    "mechanic": {
        "specialties": ["Diesel", "Auto", "Aircraft", "Marine", "Motorcycle"],
        "jokes": [
            "{specialty} Mechanic: I fix things your YouTube video couldn't",
            "{specialty} Mechanic: Cars don't need therapy, they need me",
            "{specialty} Mechanic: Grease is my glitter",
            "{specialty} Mechanic: I know what that noise is",
            "{specialty} Mechanic: Yes, it's going to cost that much",
        ]
    },
    "firefighter": {
        "specialties": ["Wildland", "Structural", "Paramedic", "EMT"],
        "jokes": [
            "{specialty} Firefighter: Running towards what you run from",
            "{specialty} Firefighter: Eat, sleep, save lives, repeat",
            "{specialty} Firefighter: My office has better views than yours",
            "{specialty} Firefighter wife/husband: Married to a hero",
        ]
    },
    "dispatcher": {
        "specialties": ["911", "Police", "Fire", "EMS"],
        "jokes": [
            "{specialty} Dispatcher: The voice of calm in chaos",
            "{specialty} Dispatcher: I've heard it all",
            "{specialty} Dispatcher: Sending help before you finish the sentence",
            "{specialty} Dispatcher: Yes, we're recording this",
        ]
    },
    "trucker": {
        "specialties": ["OTR", "Local", "Flatbed", "Tanker", "Reefer"],
        "jokes": [
            "{specialty} Trucker: Miles ahead of the rest",
            "{specialty} Trucker: My office has the best views",
            "{specialty} Trucker: Keeping America moving",
            "{specialty} Trucker wife: Married to the road",
        ]
    },
    "welder": {
        "specialties": ["MIG", "TIG", "Stick", "Pipe", "Underwater"],
        "jokes": [
            "{specialty} Welder: We join things together better than your relationships",
            "{specialty} Welder: Playing with fire is my job",
            "{specialty} Welder: I make sparks fly",
            "{specialty} Welder: Hot stuff coming through",
        ]
    },
    "phlebotomist": {
        "specialties": ["Hospital", "Lab", "Blood Bank"],
        "jokes": [
            "Phlebotomist: Yes, I'm a professional vampire",
            "Phlebotomist: I have a bloody good job",
            "Phlebotomist: I promise to make this quick",
            "Phlebotomist: Your veins are calling me",
        ]
    },
    "bartender": {
        "specialties": ["Dive Bar", "Craft Cocktail", "Sports Bar", "Club"],
        "jokes": [
            "{specialty} Bartender: Cheaper than a therapist",
            "Bartender: I've heard worse excuses",
            "Bartender: My job is all about the pour decisions",
            "{specialty} Bartender: Serving attitude since day one",
        ]
    },
}

# =============================================================================
# HOBBIES - Specific combinations
# =============================================================================
HOBBIES = {
    "fishing": {
        "types": ["Bass", "Fly", "Ice", "Deep Sea", "Kayak", "Catfish", "Trout", "Salmon", "Crappie"],
        "jokes": [
            "{type} Fishing: My therapy is measured in pounds",
            "{type} Fishing: Reel obsessed",
            "{type} Fishing Dad: Teaching patience one cast at a time",
            "{type} Fishing: Work is for people who don't fish",
            "I'd rather be {type} fishing",
            "{type} Fishing: Where the fish tales begin",
        ]
    },
    "hunting": {
        "types": ["Deer", "Duck", "Turkey", "Elk", "Bow", "Rifle"],
        "jokes": [
            "{type} Hunting: My happy place has no cell service",
            "{type} Hunting Dad: Teaching tradition one season at a time",
            "{type} Hunting: 5am alarm? No problem",
            "{type} Season: My favorite time of year",
        ]
    },
    "gaming": {
        "types": ["PC", "Console", "Retro", "RPG", "FPS", "Simulation"],
        "jokes": [
            "{type} Gamer Dad: Respawning since becoming a parent",
            "{type} Gamer Mom: Defeating bosses in game and in life",
            "{type} Gamer: I paused my game to be here",
            "{type} Gamer: AFK - Away From Kids",
            "{type} Gaming: Social distancing since before it was cool",
        ]
    },
    "gardening": {
        "types": ["Vegetable", "Flower", "Succulent", "Houseplant", "Rose", "Tomato"],
        "jokes": [
            "{type} Garden: Where I go to talk to myself",
            "{type} Gardener: My plants are my children",
            "{type} Garden: Dirty hands, clean soul",
            "{type} Gardener: I wet my plants",
            "Crazy {type} Plant Lady/Man",
        ]
    },
    "woodworking": {
        "types": ["DIY", "Furniture", "Carving", "Turning", "Cabinet"],
        "jokes": [
            "{type} Woodworker: Measure twice, cut once, swear repeatedly",
            "{type} Woodworking: Sawdust is man glitter",
            "{type} Woodworker: I make things out of trees",
            "{type} Woodworking Dad: Building memories",
        ]
    },
    "quilting": {
        "types": ["Traditional", "Modern", "Art", "Hand", "Machine"],
        "jokes": [
            "{type} Quilter: Yes, I need more fabric",
            "{type} Quilting: My fabric stash has a fabric stash",
            "{type} Quilter: Sew much fabric, sew little time",
            "{type} Quilting: Piecing it all together",
        ]
    },
    "crocheting": {
        "types": ["Amigurumi", "Blanket", "Wearable"],
        "jokes": [
            "Crocheter: Yes, I need more yarn",
            "Crocheting: One skein away from insanity",
            "Crochet: Hooked since day one",
            "Crocheter: Making knots look good",
        ]
    },
    "camping": {
        "types": ["Tent", "RV", "Backpacking", "Glamping", "Car"],
        "jokes": [
            "{type} Camping: Home is where you pitch it",
            "{type} Camper: I don't need therapy, I need camping",
            "{type} Camping: Where WiFi is weak but connection is strong",
            "{type} Camping Family: Making memories in the wilderness",
        ]
    },
    "motorcycles": {
        "types": ["Harley", "Sportbike", "Cruiser", "Dirt Bike", "Adventure"],
        "jokes": [
            "{type} Rider: Two wheels, one love",
            "{type} Motorcycle: Cheaper than therapy",
            "{type} Biker Dad: Teaching balance in life",
            "{type} Rider: My therapist has two wheels",
            "{type} Life: Four wheels move the body, two wheels move the soul",
        ]
    },
}

# =============================================================================
# IDENTITY COMBINATIONS
# =============================================================================
IDENTITIES = ["Mom", "Dad", "Grandma", "Grandpa", "Wife", "Husband", "Parent", "Owner", "Lover"]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dog_breed_designs(breed_key, count=5):
    """Generate design ideas for a specific dog breed."""
    breed = DOG_BREEDS.get(breed_key, {})
    if not breed:
        return []

    designs = []
    breed_name = breed['names'][0]

    for joke in breed.get('jokes', [])[:count]:
        for identity in ['Mom', 'Dad', 'Parent', 'Owner']:
            designs.append({
                'niche': 'dogs',
                'sub_niche': breed_name,
                'identity': identity,
                'quote': joke,
                'tags': [breed_key.replace('_', ' '), breed_name.lower(), f'{breed_name.lower()} {identity.lower()}', 'dog lover', 'dog gift'],
            })

    return designs


def get_profession_designs(profession_key, count=5):
    """Generate design ideas for a specific profession."""
    profession = PROFESSIONS.get(profession_key, {})
    if not profession:
        return []

    designs = []

    for specialty in profession.get('specialties', [''])[:3]:
        for joke_template in profession.get('jokes', [])[:count]:
            joke = joke_template.format(specialty=specialty) if '{specialty}' in joke_template else joke_template
            designs.append({
                'niche': 'professions',
                'sub_niche': profession_key,
                'specialty': specialty,
                'quote': joke,
                'tags': [profession_key, specialty.lower() if specialty else '', 'career', 'work humor'],
            })

    return designs


def get_hobby_designs(hobby_key, count=5):
    """Generate design ideas for a specific hobby."""
    hobby = HOBBIES.get(hobby_key, {})
    if not hobby:
        return []

    designs = []

    for hobby_type in hobby.get('types', [''])[:3]:
        for joke_template in hobby.get('jokes', [])[:count]:
            joke = joke_template.format(type=hobby_type) if '{type}' in joke_template else joke_template
            for identity in ['Dad', 'Mom', 'Enthusiast']:
                designs.append({
                    'niche': 'hobbies',
                    'sub_niche': hobby_key,
                    'type': hobby_type,
                    'identity': identity,
                    'quote': joke,
                    'tags': [hobby_key, hobby_type.lower(), f'{hobby_key} {identity.lower()}', 'hobby gift'],
                })

    return designs


def get_all_micro_niches():
    """Get counts of all available micro-niches."""
    return {
        'dog_breeds': len(DOG_BREEDS),
        'cat_breeds': len(CAT_BREEDS),
        'professions': len(PROFESSIONS),
        'hobbies': len(HOBBIES),
        'total_combinations': (
            sum(len(b.get('jokes', [])) for b in DOG_BREEDS.values()) * len(IDENTITIES) +
            sum(len(p.get('jokes', [])) * len(p.get('specialties', [])) for p in PROFESSIONS.values()) +
            sum(len(h.get('jokes', [])) * len(h.get('types', [])) for h in HOBBIES.values())
        )
    }


if __name__ == "__main__":
    stats = get_all_micro_niches()
    print("MICRO-NICHE DATABASE")
    print("=" * 40)
    print(f"Dog Breeds:      {stats['dog_breeds']}")
    print(f"Cat Breeds:      {stats['cat_breeds']}")
    print(f"Professions:     {stats['professions']}")
    print(f"Hobbies:         {stats['hobbies']}")
    print(f"Total Combos:    {stats['total_combinations']:,}+")
    print("\nSample Designs:")
    print("-" * 40)

    # Sample from each category
    designs = get_dog_breed_designs('corgi', 2)
    for d in designs[:2]:
        print(f"[DOG] {d['quote']}")

    designs = get_profession_designs('nurse', 2)
    for d in designs[:2]:
        print(f"[JOB] {d['quote']}")

    designs = get_hobby_designs('fishing', 2)
    for d in designs[:2]:
        print(f"[HOBBY] {d['quote']}")
