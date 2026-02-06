# Deploy to GitHub Pages (Free Hosting)

## One-Time Setup (5 minutes)

### Step 1: Create GitHub Repository

Go to https://github.com/new and create a new repo called `knowledge-base`

### Step 2: Initialize and Push

```bash
cd "E:\Projects\Blog template\asset-generator"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Self-propagating Knowledge Factory"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/knowledge-base.git

# Push
git branch -M main
git push -u origin main
```

### Step 3: Add API Key Secret

1. Go to your repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GOOGLE_API_KEY`
5. Value: Your Gemini API key
6. Click **Add secret**

### Step 4: Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Save

### Step 5: Update Workflow for GitHub Pages

The workflow will auto-deploy. Your site will be live at:

```
https://YOUR_USERNAME.github.io/knowledge-base/
```

---

## How It Works After Setup

```
Every day at 3 AM UTC:
    │
    ├── GitHub Action triggers
    │
    ├── Generates 10 new pages
    │
    ├── Commits to repo
    │
    └── GitHub Pages auto-deploys
         │
         └── Site updated with new content
```

**You do nothing.** It runs forever.

---

## Manual Trigger

To generate pages manually:

1. Go to repo → **Actions** → **Self-Propagating Knowledge Pages**
2. Click **Run workflow**
3. Set count (e.g., 20)
4. Click **Run workflow**

---

## Monitor Progress

Check the Actions tab to see:
- Generation logs
- Success/failure status
- Pages created

---

## Custom Domain (Optional)

1. Buy a domain (e.g., Namecheap, ~$10/year)
2. In repo Settings → Pages → Custom domain
3. Enter your domain
4. Add DNS records as instructed
5. Enable "Enforce HTTPS"

Your site: `https://yourdomain.com`

---

## Costs

| Item | Cost |
|------|------|
| GitHub Pages hosting | Free |
| GitHub Actions | Free (2,000 min/month) |
| Gemini API (Pro) | ~$20/month |
| Domain (optional) | ~$10/year |

**Total: $0-20/month**

---

## Revenue Setup

Once you have traffic:

### Google AdSense
1. Apply at https://adsense.google.com
2. Add ad code to page template
3. Earn $1-30 per 1,000 pageviews

### Affiliate Links
Add relevant affiliate links in content:
- Finance pages → Brokerage links
- Math pages → Calculator tool links
- etc.

---

## Scaling

| Pages | Expected Monthly Traffic | Estimated Revenue |
|-------|-------------------------|-------------------|
| 100 | 1K-5K | $10-50 |
| 500 | 10K-50K | $100-500 |
| 2,000 | 50K-200K | $500-2,000 |
| 10,000 | 200K-1M | $2,000-10,000 |

At 10 pages/day = 3,650 pages/year
