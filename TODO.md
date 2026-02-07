# TODO - 360library.com

## MUST READ - Monetization

When the site has grown (10,000+ pages, consistent traffic):

### 1. Google AdSense
- Apply at: https://www.google.com/adsense
- Requirements: Original content, privacy policy, good UX
- Add ads.txt to generated_pages/
- Insert ad code into HTML templates in knowledge_pages.py

### 2. Alternative Ad Networks (if AdSense rejected)
- **Ezoic** - Good for smaller sites, AI-optimized ads
- **Mediavine** - Requires 50k sessions/month
- **AdThrive** - Premium, requires 100k pageviews/month

### 3. Implementation Steps
1. Add privacy policy page (required for ads)
2. Add cookie consent banner
3. Modify HTML template to include ad slots:
   - After first paragraph
   - Sidebar (if added)
   - End of article
4. Update generate_sitemap.py to include new pages

### 4. Other Monetization Ideas
- Affiliate links for related products/services
- Premium API access for B2B licensing
- Dataset licensing for AI training

---

## Current Status
- **Domains closed:** 5 (finance, life_obligations, science, math, economics)
- **Domains in queue:** 12 (health processing + 11 pending)
- **Auto-discovery:** Enabled (refills when < 3 pending)
- **Daily automation:** 3 AM UTC, 200 pages/day

## Site
- URL: https://360library.com
- Sitemap: https://360library.com/sitemap.xml
- Google Search Console: Submitted
