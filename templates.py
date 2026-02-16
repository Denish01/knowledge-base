"""
Shared templates for 360Library.com
Header, footer, sidebar, breadcrumbs, and CSS constants.
"""

# =============================================================================
# DOMAIN METADATA
# =============================================================================

DOMAIN_META = {
    "economics": {
        "name": "Economics",
        "color": "#059669",
        "icon": "📊",
        "description": "Explore economic concepts, theories, and real-world applications.",
    },
    "finance": {
        "name": "Finance",
        "color": "#1B4D8E",
        "icon": "💰",
        "description": "Personal finance, investing, and financial planning made simple.",
    },
    "health": {
        "name": "Health",
        "color": "#DC2626",
        "icon": "🏥",
        "description": "Health topics, medical concepts, and wellness explained clearly.",
    },
    "life_obligations": {
        "name": "Life Obligations",
        "color": "#7C3AED",
        "icon": "📋",
        "description": "Legal obligations, family law, benefits, and civic responsibilities.",
    },
    "math": {
        "name": "Math",
        "color": "#D97706",
        "icon": "🔢",
        "description": "Mathematical concepts from basics to advanced, explained simply.",
    },
    "science": {
        "name": "Science",
        "color": "#0891B2",
        "icon": "🔬",
        "description": "Scientific principles, natural phenomena, and discoveries.",
    },
}

# Domains that use flat file layout (files directly in domain folder, not in concept subdirs)
FLAT_DOMAINS = {"health"}


def flat_angle_to_filename(concept, angle):
    """Convert (concept, angle_id) to the flat filename stem.

    E.g. ('oncology', 'types-of') -> 'types-of-oncology'
         ('oncology', 'what-is') -> 'oncology'
         ('oncology', 'vs') -> 'oncology-vs'
    """
    mapping = {
        "what-is": concept,
        "vs": f"{concept}-vs",
        "common-misconceptions-about": f"common-misconceptions-about-{concept}",
        "example-of": f"examples-of-{concept}",
        "types-of": f"types-of-{concept}",
        "how-it-works": f"how-does-{concept}-work",
        "what-affects-it": f"what-affects-{concept}",
        "what-it-depends-on": f"what-{concept}-depends-on",
    }
    return mapping.get(angle, f"{concept}-{angle}")


def angle_url(domain_slug, concept_slug, angle):
    """Build the correct URL for an angle page, handling flat vs structured domains."""
    if domain_slug in FLAT_DOMAINS:
        filename = flat_angle_to_filename(concept_slug, angle)
        return f"/{domain_slug}/{filename}.html"
    return f"/{domain_slug}/{concept_slug}/{angle}.html"


ANGLE_DISPLAY = {
    "what-is": "What Is",
    "how-it-works": "How It Works",
    "example-of": "Example",
    "types-of": "Types",
    "common-misconceptions-about": "Misconceptions",
    "what-affects-it": "What Affects It",
    "what-it-depends-on": "What It Depends On",
    "vs": "Comparison",
}

# =============================================================================
# CSS CONSTANTS
# =============================================================================

SHARED_CSS = """
/* === Reset & Base === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: #1F2937;
    background: #FAFBFC;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}
a { color: #1B4D8E; text-decoration: none; }
a:hover { text-decoration: underline; }

/* === Header === */
.site-header {
    background: #1B4D8E;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 60px;
}
.site-logo {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    letter-spacing: -0.5px;
}
.site-logo:hover { text-decoration: none; opacity: 0.9; }
.site-logo span { color: #D97706; }

/* Domain nav */
.domain-nav { display: flex; gap: 4px; list-style: none; }
.domain-nav a {
    color: rgba(255,255,255,0.85);
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.2s, color 0.2s;
    text-decoration: none;
    white-space: nowrap;
}
.domain-nav a:hover { background: rgba(255,255,255,0.15); color: #fff; text-decoration: none; }
.domain-nav a.active { background: rgba(255,255,255,0.2); color: #fff; }

/* Mobile hamburger (pure CSS) */
.menu-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
.menu-toggle span, .menu-toggle span::before, .menu-toggle span::after {
    display: block; width: 22px; height: 2px; background: #fff; position: relative; transition: 0.3s;
}
.menu-toggle span::before, .menu-toggle span::after { content: ''; position: absolute; left: 0; }
.menu-toggle span::before { top: -7px; }
.menu-toggle span::after { top: 7px; }
#mobile-menu-state { display: none; }

@media (max-width: 768px) {
    .menu-toggle { display: block; }
    .domain-nav {
        display: none; flex-direction: column; position: absolute;
        top: 60px; left: 0; right: 0; background: #1B4D8E;
        padding: 12px; gap: 2px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .domain-nav a { padding: 12px 16px; border-radius: 8px; }
    #mobile-menu-state:checked ~ .header-inner .domain-nav { display: flex; }
}

/* === Footer === */
.site-footer {
    background: #111827;
    color: #9CA3AF;
    margin-top: 80px;
    padding: 48px 24px 32px;
}
.footer-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 40px;
}
.footer-brand .site-logo { font-size: 18px; display: inline-block; margin-bottom: 12px; }
.footer-brand p { font-size: 14px; line-height: 1.6; max-width: 320px; }
.footer-col h4 { color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
.footer-col a { display: block; color: #9CA3AF; font-size: 14px; padding: 4px 0; transition: color 0.2s; text-decoration: none; }
.footer-col a:hover { color: #fff; text-decoration: none; }
.footer-bottom {
    max-width: 1200px;
    margin: 32px auto 0;
    padding-top: 24px;
    border-top: 1px solid #374151;
    text-align: center;
    font-size: 13px;
}

@media (max-width: 768px) {
    .footer-inner { grid-template-columns: 1fr; gap: 32px; }
}

/* === Breadcrumbs === */
.breadcrumbs {
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px 24px;
    font-size: 14px;
    color: #6B7280;
}
.breadcrumbs a { color: #1B4D8E; }
.breadcrumbs span { margin: 0 8px; color: #D1D5DB; }
"""

HOMEPAGE_CSS = """
/* === Hero === */
.hero {
    background: linear-gradient(135deg, #1B4D8E 0%, #1e3a5f 100%);
    color: #fff;
    padding: 72px 24px;
    text-align: center;
}
.hero h1 { font-size: 42px; font-weight: 700; margin-bottom: 16px; letter-spacing: -1px; }
.hero p { font-size: 18px; opacity: 0.9; max-width: 600px; margin: 0 auto 32px; line-height: 1.6; }
.hero-stats {
    display: flex; justify-content: center; gap: 48px; margin-top: 24px;
}
.hero-stat { text-align: center; }
.hero-stat .num { font-size: 32px; font-weight: 700; display: block; }
.hero-stat .label { font-size: 14px; opacity: 0.8; }

@media (max-width: 768px) {
    .hero { padding: 48px 20px; }
    .hero h1 { font-size: 28px; }
    .hero p { font-size: 16px; }
    .hero-stats { gap: 24px; }
    .hero-stat .num { font-size: 24px; }
}

/* === Domain Cards === */
.domain-cards-section {
    max-width: 1200px;
    margin: -40px auto 0;
    padding: 0 24px;
    position: relative;
    z-index: 10;
}
.domain-cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}
.domain-card {
    background: #fff;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-top: 4px solid var(--domain-color);
    transition: transform 0.2s, box-shadow 0.2s;
}
.domain-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.domain-card-icon { font-size: 32px; margin-bottom: 12px; }
.domain-card h3 { font-size: 18px; font-weight: 700; color: #1F2937; margin-bottom: 6px; }
.domain-card .card-meta { font-size: 13px; color: #6B7280; margin-bottom: 12px; }
.domain-card p { font-size: 14px; color: #4B5563; line-height: 1.6; margin-bottom: 16px; }
.domain-card .explore-link {
    display: inline-block;
    font-size: 14px;
    font-weight: 600;
    color: var(--domain-color);
}
.domain-card .explore-link:hover { text-decoration: underline; }

@media (max-width: 768px) {
    .domain-cards-grid { grid-template-columns: 1fr; }
    .domain-cards-section { margin-top: -24px; }
}
@media (min-width: 769px) and (max-width: 1024px) {
    .domain-cards-grid { grid-template-columns: repeat(2, 1fr); }
}

/* === Concept Grids === */
.concepts-section {
    max-width: 1200px;
    margin: 64px auto;
    padding: 0 24px;
}
.domain-section { margin-bottom: 56px; }
.domain-section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid #E5E7EB;
}
.domain-section-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #1F2937;
}
.domain-section-header .badge {
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    color: #fff;
}
.concept-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}
.concept-card {
    background: #fff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #E5E7EB;
    transition: box-shadow 0.2s;
}
.concept-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.concept-card h3 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
}
.concept-card h3 a { color: #1F2937; }
.concept-card h3 a:hover { color: #1B4D8E; }
.angle-links {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.angle-link {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 6px;
    background: #F3F4F6;
    color: #4B5563;
    transition: background 0.2s, color 0.2s;
    text-decoration: none;
}
.angle-link:hover {
    background: #E8F0FE;
    color: #1B4D8E;
    text-decoration: none;
}
"""

ARTICLE_CSS = """
/* === Article Layout === */
.article-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 24px 0;
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 40px;
    align-items: start;
}

/* Main content */
.article-main { min-width: 0; }
.article-main article {
    background: #fff;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #E5E7EB;
}
.article-main h1 {
    font-size: 32px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 24px;
    line-height: 1.3;
}
.article-main h2 {
    font-size: 22px;
    font-weight: 700;
    color: #1F2937;
    margin-top: 36px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #E8F0FE;
}
.article-main h3 {
    font-size: 18px;
    font-weight: 600;
    color: #374151;
    margin-top: 28px;
    margin-bottom: 12px;
}
.article-main p {
    margin-bottom: 16px;
    color: #374151;
}
.article-main ul {
    padding-left: 24px;
    margin-bottom: 16px;
}
.article-main li {
    margin-bottom: 8px;
    color: #374151;
}
.article-main table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    font-size: 14px;
}
.article-main th, .article-main td {
    border: 1px solid #E5E7EB;
    padding: 12px 16px;
    text-align: left;
}
.article-main th {
    background: #F9FAFB;
    font-weight: 600;
    color: #1F2937;
}
.article-main tr:nth-child(even) { background: #F9FAFB; }

/* Calculator styles (preserve existing) */
.article-main .calculator,
.article-main .calc-container {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 24px;
    margin: 24px 0;
}

/* === Sidebar === */
.article-sidebar {
    position: sticky;
    top: 76px;
}
.sidebar-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #E5E7EB;
}
.sidebar-card h3 {
    font-size: 15px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #E8F0FE;
}
.sidebar-card .angle-nav { list-style: none; }
.sidebar-card .angle-nav li { margin-bottom: 4px; }
.sidebar-card .angle-nav a {
    display: block;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 14px;
    color: #4B5563;
    transition: background 0.2s, color 0.2s;
    text-decoration: none;
}
.sidebar-card .angle-nav a:hover {
    background: #F3F4F6;
    color: #1B4D8E;
    text-decoration: none;
}
.sidebar-card .angle-nav a.active {
    background: #E8F0FE;
    color: #1B4D8E;
    font-weight: 600;
}

/* Back to domain link */
.sidebar-card .back-link {
    display: block;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #E5E7EB;
    font-size: 13px;
    color: #6B7280;
}
.sidebar-card .back-link:hover { color: #1B4D8E; text-decoration: none; }

@media (max-width: 900px) {
    .article-wrapper {
        grid-template-columns: 1fr;
        padding: 16px 16px 0;
    }
    .article-sidebar {
        position: static;
        order: -1;
    }
    .article-main article { padding: 24px; }
    .article-main h1 { font-size: 24px; }
}
"""

# =============================================================================
# HTML GENERATORS
# =============================================================================

def generate_header_html(active_domain=None):
    """Generate sticky header with logo and domain nav."""
    nav_items = ""
    for slug, meta in DOMAIN_META.items():
        active_cls = ' class="active"' if slug == active_domain else ""
        display = meta["name"]
        nav_items += f'        <li><a href="/#{slug}"{active_cls}>{display}</a></li>\n'

    return f"""<input type="checkbox" id="mobile-menu-state" aria-hidden="true">
<header class="site-header">
    <div class="header-inner">
        <a href="/" class="site-logo">360 <span>Library</span></a>
        <label for="mobile-menu-state" class="menu-toggle" aria-label="Toggle menu"><span></span></label>
        <ul class="domain-nav">
{nav_items}        </ul>
    </div>
</header>"""


def generate_footer_html():
    """Generate 3-column dark footer."""
    domain_links = ""
    for slug, meta in DOMAIN_META.items():
        domain_links += f'            <a href="/#{slug}">{meta["name"]}</a>\n'

    return f"""<footer class="site-footer">
    <div class="footer-inner">
        <div class="footer-brand">
            <a href="/" class="site-logo">360 <span>Library</span></a>
            <p>Free encyclopedic reference covering economics, finance, health, life obligations, math, and science. Every concept explained from multiple angles.</p>
        </div>
        <div class="footer-col">
            <h4>Domains</h4>
{domain_links}        </div>
        <div class="footer-col">
            <h4>Info</h4>
            <a href="/privacy.html">Privacy Policy</a>
            <a href="/terms.html">Terms of Use</a>
            <a href="/sitemap.xml">Sitemap</a>
        </div>
    </div>
    <div class="footer-bottom">
        &copy; 2026 360Library.com &mdash; All rights reserved.
    </div>
</footer>"""


def generate_breadcrumb_html(domain_slug, concept_slug, angle_id):
    """Generate breadcrumb trail: Home > Domain > Concept > Angle."""
    domain_name = DOMAIN_META.get(domain_slug, {}).get("name", domain_slug.replace("_", " ").title())
    concept_display = concept_slug.replace("-", " ").title()
    angle_display = ANGLE_DISPLAY.get(angle_id, angle_id.replace("-", " ").title())
    concept_href = angle_url(domain_slug, concept_slug, "what-is")

    return f"""<nav class="breadcrumbs" aria-label="Breadcrumb">
    <a href="/">Home</a><span>&rsaquo;</span><a href="/#{domain_slug}">{domain_name}</a><span>&rsaquo;</span><a href="{concept_href}">{concept_display}</a><span>&rsaquo;</span>{angle_display}
</nav>"""


def generate_sidebar_html(domain_slug, concept_slug, current_angle, all_angles):
    """Generate sidebar with angle navigation for current concept."""
    domain_name = DOMAIN_META.get(domain_slug, {}).get("name", domain_slug.replace("_", " ").title())
    concept_display = concept_slug.replace("-", " ").title()

    links = ""
    # Sort angles in canonical order
    ordered = []
    canonical_order = ["what-is", "how-it-works", "example-of", "types-of",
                       "common-misconceptions-about", "what-affects-it",
                       "what-it-depends-on", "vs"]
    for angle in canonical_order:
        if angle in all_angles:
            ordered.append(angle)
    # Any remaining angles not in canonical order
    for angle in sorted(all_angles):
        if angle not in ordered:
            ordered.append(angle)

    for angle in ordered:
        display = ANGLE_DISPLAY.get(angle, angle.replace("-", " ").title())
        active_cls = ' class="active"' if angle == current_angle else ""
        href = angle_url(domain_slug, concept_slug, angle)
        links += f'            <li><a href="{href}"{active_cls}>{display}</a></li>\n'

    return f"""<aside class="article-sidebar">
    <div class="sidebar-card">
        <h3>{concept_display}</h3>
        <ul class="angle-nav">
{links}        </ul>
        <a href="/#{domain_slug}" class="back-link">&larr; All {domain_name} concepts</a>
    </div>
</aside>"""
