"""
Generate Privacy Policy and Terms of Use pages for 360Library.com
"""
from pathlib import Path
from templates import SHARED_CSS, ARTICLE_CSS, generate_header_html, generate_footer_html, generate_og_tags

OUTPUT_DIR = Path(__file__).parent / "generated_pages"

CONTACT_EMAIL = "mrgovernment02@gmail.com"

PRIVACY_CONTENT = f"""\
<h1>Privacy Policy</h1>
<p><strong>Last updated:</strong> February 16, 2026</p>

<h2>Introduction</h2>
<p>360Library.com ("we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard information when you visit our website at <a href="https://360library.com">https://360library.com</a>.</p>

<h2>Information We Collect</h2>
<h3>Automatically Collected Information</h3>
<p>When you visit 360Library.com, our hosting provider (GitHub Pages) may automatically collect certain technical information, including:</p>
<ul>
    <li>IP address</li>
    <li>Browser type and version</li>
    <li>Pages visited and time spent</li>
    <li>Referring website</li>
</ul>

<h3>Analytics</h3>
<p>We may use third-party analytics services (such as Google Analytics) to understand how visitors use our site. These services may collect anonymized data about your browsing behavior. You can opt out of Google Analytics by installing the <a href="https://tools.google.com/dlpage/gaoptout" rel="nofollow">Google Analytics Opt-out Browser Add-on</a>.</p>

<h3>Personal Information</h3>
<p>We do not require you to create an account or provide personal information to use 360Library.com. If you contact us via email at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>, we will only use your information to respond to your inquiry.</p>

<h2>How We Use Information</h2>
<p>Any information collected is used solely to:</p>
<ul>
    <li>Operate and maintain the website</li>
    <li>Understand usage patterns to improve content</li>
    <li>Respond to inquiries</li>
</ul>

<h2>Cookies</h2>
<p>360Library.com does not set first-party cookies. Third-party services (such as analytics providers) may set cookies. You can control cookies through your browser settings.</p>

<h2>Third-Party Links</h2>
<p>Our content may contain links to external websites. We are not responsible for the privacy practices of those sites and encourage you to read their privacy policies.</p>

<h2>Children's Privacy</h2>
<p>360Library.com is an educational reference site suitable for all ages. We do not knowingly collect personal information from children under 13.</p>

<h2>Data Security</h2>
<p>360Library.com is a static website hosted on GitHub Pages. We do not store user data on our own servers. All content is served over HTTPS.</p>

<h2>Changes to This Policy</h2>
<p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated date.</p>

<h2>Contact Us</h2>
<p>If you have questions about this Privacy Policy, please contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
"""

TERMS_CONTENT = f"""\
<h1>Terms of Use</h1>
<p><strong>Last updated:</strong> February 16, 2026</p>

<h2>Acceptance of Terms</h2>
<p>By accessing and using 360Library.com ("the Site"), you agree to be bound by these Terms of Use. If you do not agree, please do not use the Site.</p>

<h2>About 360Library.com</h2>
<p>360Library.com is a free encyclopedic reference providing educational content across multiple knowledge domains including economics, finance, health, life obligations, math, and science.</p>

<h2>Use of Content</h2>
<h3>Educational Purpose</h3>
<p>All content on 360Library.com is provided for general educational and informational purposes only. Content should not be considered as professional, medical, legal, financial, or other specialized advice.</p>

<h3>No Professional Advice</h3>
<ul>
    <li><strong>Health content</strong> is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.</li>
    <li><strong>Finance content</strong> is not financial advice. Consult a licensed financial advisor for personal financial decisions.</li>
    <li><strong>Legal content</strong> (including life obligations) is not legal advice. Consult a qualified attorney for legal matters.</li>
</ul>

<h3>Permitted Use</h3>
<p>You may freely access, read, and share links to content on 360Library.com for personal, educational, and non-commercial purposes.</p>

<h2>AI-Generated Content</h2>
<p>Content on 360Library.com is generated with the assistance of artificial intelligence and reviewed for accuracy. While we strive for factual correctness, we cannot guarantee that all information is complete, current, or error-free. We encourage readers to verify important information through additional sources.</p>

<h2>Intellectual Property</h2>
<p>The content, design, and branding of 360Library.com are the property of 360Library.com. You may not reproduce, distribute, or create derivative works from our content for commercial purposes without permission.</p>

<h2>Disclaimer of Warranties</h2>
<p>The Site is provided "as is" and "as available" without warranties of any kind, either express or implied. We do not warrant that the Site will be uninterrupted, error-free, or free of harmful components.</p>

<h2>Limitation of Liability</h2>
<p>To the fullest extent permitted by law, 360Library.com shall not be liable for any damages arising from your use of or inability to use the Site or its content.</p>

<h2>External Links</h2>
<p>The Site may contain links to third-party websites. We are not responsible for the content or practices of linked sites.</p>

<h2>Changes to Terms</h2>
<p>We reserve the right to modify these Terms of Use at any time. Continued use of the Site after changes constitutes acceptance of the updated terms.</p>

<h2>Contact</h2>
<p>For questions about these Terms of Use, please contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
"""


def generate_legal_page(title, meta_desc, content_html, canonical_path):
    header = generate_header_html()
    footer = generate_footer_html()
    og_tags = generate_og_tags(title, meta_desc, f"https://360library.com/{canonical_path}")
    canonical_tag = f'<link rel="canonical" href="https://360library.com/{canonical_path}">'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    {canonical_tag}
    {og_tags}
    <title>{title} - 360Library</title>
    <style>
{SHARED_CSS}
{ARTICLE_CSS}
    </style>
</head>
<body>
{header}

<div class="article-wrapper">
    <main class="article-main">
        <article>
            {content_html}
        </article>
    </main>
</div>

{footer}
</body>
</html>
"""


def main():
    # Privacy Policy
    privacy_html = generate_legal_page(
        "Privacy Policy",
        "360Library.com Privacy Policy — how we collect, use, and protect your information.",
        PRIVACY_CONTENT,
        "privacy.html",
    )
    privacy_path = OUTPUT_DIR / "privacy.html"
    privacy_path.write_text(privacy_html, encoding="utf-8")
    print(f"Written: {privacy_path}")

    # Terms of Use
    terms_html = generate_legal_page(
        "Terms of Use",
        "360Library.com Terms of Use — rules and guidelines for using our educational reference site.",
        TERMS_CONTENT,
        "terms.html",
    )
    terms_path = OUTPUT_DIR / "terms.html"
    terms_path.write_text(terms_html, encoding="utf-8")
    print(f"Written: {terms_path}")


if __name__ == "__main__":
    main()
