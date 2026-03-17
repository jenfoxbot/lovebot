# LoveBot Technical Specification

## Overview

A Bluesky bot that posts daily morning content about love, using AI-assisted content generation with human approval.

**Platform:** Bluesky  
**Handle:** `lovebotdaily.bsky.social`  
**Budget:** $0 (free tools only)  
**Posting:** 6:00 AM PST daily  
**Timezone:** PST (UTC-8)  
**Content Generation:** VS Code Copilot (weekly batches)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTENT CREATION (Weekly)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [You] ──prompt──> [ChatGPT/Claude Free] ──drafts──> [You]     │
│                                                                  │
│   Review & approve posts, add to content library                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CONTENT STORAGE (GitHub)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   /content/posts.json    ← All approved posts                   │
│   /content/posted.json   ← Track what's been posted             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DAILY POSTING (GitHub Actions)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Cron: 7:00 AM daily                                           │
│                                                                  │
│   1. Read posts.json                                            │
│   2. Select next unposted content                               │
│   3. Post to Bluesky via API                                    │
│   4. Mark as posted in posted.json                              │
│   5. Commit change back to repo                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Free Tools Stack

| Component | Tool | Cost |
|-----------|------|------|
| Content Generation | VS Code Copilot | $0 (included with VS Code) |
| Content Storage | GitHub Repository | $0 |
| Scheduling & Execution | GitHub Actions | $0 (2,000 min/month free) |
| Social Platform | Bluesky API | $0 |
| Version Control | Git | $0 |

### Why This Stack Works

- **GitHub Actions** runs for free on public repositories (or 2,000 minutes/month on private)
- **Bluesky API** is completely free with no rate limits for normal posting
- **VS Code Copilot** generates content using the `.github/copilot-instructions.md` context file
- **No server needed** — entirely serverless via GitHub Actions

---

## File Structure

```
LoveBot/
├── .github/
│   ├── copilot-instructions.md # Context for Copilot content generation
│   └── workflows/
│       └── daily-post.yml      # GitHub Actions workflow
├── content/
│   ├── posts-YYYY-MM-DD.json   # Approved posts (dated by creation batch)
│   └── posted.json             # Log of posted content
├── src/
│   └── post.py                 # Python script to post to Bluesky
├── prompts/
│   ├── content-generation.md   # Reference prompts
│   └── GENERATE_WEEKLY.md      # Weekly generation workflow for Copilot
├── requirements.txt            # Python dependencies
├── PROJECT_PLAN.md
├── TECHNICAL_SPEC.md
└── README.md
```

**Note:** Post files use dated filenames (e.g., `posts-2026-02-21.json`) so you can track when each batch was created. The bot reads from all `posts-*.json` files in the content folder.

---

## Data Structures

### posts-YYYY-MM-DD.json

Each batch of posts is stored in a dated file (e.g., `posts-2026-02-21.json`).

**Important:** The `content` field should include the attribution/source as part of the text, since this is exactly what gets posted to Bluesky.

```json
{
  "posts": [
    {
      "id": "001",
      "content": "Love is not something we fall into. It's something we choose—and keep choosing—through care, presence, and the courage to show up.\n\n— Inspired by M. Scott Peck",
      "source": "Inspired by M. Scott Peck",
      "pillar": "commitment",
      "type": "reflection",
      "hashtags": ["DailyLove", "Commitment", "ShowUp"],
      "created_date": "2026-02-21",
      "posted": false,
      "posted_date": null
    },
    {
      "id": "002",
      "content": "\"Knowing that we can be loved exactly as we are gives us all the best opportunity for growing into the healthiest of people.\"\n\n— Fred Rogers",
      "source": "Fred Rogers",
      "pillar": "trust",
      "type": "quote",
      "hashtags": ["LoveReminder", "Trust", "LoveQuotes"],
      "created_date": "2026-02-21",
      "posted": false,
      "posted_date": null
    }
  ]
}
```

### posted.json
```json
{
  "log": [
    {
      "id": "001",
      "posted_date": "2026-02-22T07:00:00Z",
      "bluesky_uri": "at://did:plc:xxx/app.bsky.feed.post/xxx"
    }
  ],
  "last_posted_index": 0,
  "total_posted": 1
}
```

---

## Bluesky Setup

### 1. Create Account
1. ✅ Account created: `lovebotdaily.bsky.social`
2. Complete profile setup (bio, avatar)

### 2. Create App Password
1. Go to Settings → App Passwords
2. Create new app password (name it "LoveBot")
3. Save the password securely — you'll need it for GitHub Secrets

### 3. Store Credentials in GitHub
Add these as Repository Secrets (Settings → Secrets and variables → Actions):
- `BLUESKY_HANDLE`: `lovebotdaily.bsky.social`
- `BLUESKY_APP_PASSWORD`: The app password you created

---

## GitHub Actions Workflow

### .github/workflows/daily-post.yml
```yaml
name: Daily Love Post

on:
  schedule:
    # Runs at 6:00 AM PST (14:00 UTC) every day
    - cron: '0 14 * * *'
  workflow_dispatch:  # Allows manual trigger for testing

jobs:
  post:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Post to Bluesky
        env:
          BLUESKY_HANDLE: ${{ secrets.BLUESKY_HANDLE }}
          BLUESKY_APP_PASSWORD: ${{ secrets.BLUESKY_APP_PASSWORD }}
        run: python src/post.py
      
      - name: Commit posted.json update
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add content/posted.json
          git diff --staged --quiet || git commit -m "Update posted.json after daily post"
          git push
```

---

## Python Script

### requirements.txt
```
atproto>=0.0.30
```

### src/post.py
```python
"""
LoveBot - Daily Bluesky poster
Posts one piece of content about love each day.
"""

import glob
import json
import os
from datetime import datetime, timezone
from atproto import Client

# Configuration
CONTENT_DIR = 'content'
POSTED_FILE = 'content/posted.json'


def load_json(filepath):
    """Load JSON file, return empty structure if not exists."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        if 'posted' in filepath:
            return {"log": [], "total_posted": 0}
        return {"posts": []}


def load_all_posts():
    """Load posts from all posts-*.json files in content directory."""
    all_posts = []
    pattern = os.path.join(CONTENT_DIR, 'posts-*.json')
    
    for filepath in sorted(glob.glob(pattern)):
        data = load_json(filepath)
        all_posts.extend(data.get('posts', []))
    
    return all_posts


def save_json(filepath, data):
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_post(all_posts, posted_data):
    """Get the next unposted content."""
    posted_ids = {entry['id'] for entry in posted_data.get('log', [])}
    
    for post in all_posts:
        if post['id'] not in posted_ids and not post.get('posted', False):
            return post
    
    return None


def post_to_bluesky(content: str) -> dict:
    """Post content to Bluesky and return the response."""
    handle = os.environ.get('BLUESKY_HANDLE')
    password = os.environ.get('BLUESKY_APP_PASSWORD')
    
    if not handle or not password:
        raise ValueError("Missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD environment variables")
    
    client = Client()
    client.login(handle, password)
    
    response = client.send_post(text=content)
    return response


def main():
    """Main function to post daily content."""
    # Load data
    all_posts = load_all_posts()
    posted_data = load_json(POSTED_FILE)
    
    print(f"Loaded {len(all_posts)} total posts from content/posts-*.json files")
    
    # Get next post
    next_post = get_next_post(all_posts, posted_data)
    
    if not next_post:
        print("No unposted content available! Add more posts to content/posts-YYYY-MM-DD.json")
        return
    
    print(f"Posting content ID: {next_post['id']}")
    print(f"Content: {next_post['content'][:100]}...")
    
    # Post to Bluesky
    try:
        response = post_to_bluesky(next_post['content'])
        print(f"Successfully posted! URI: {response.uri}")
        
        # Update posted.json
        posted_data['log'].append({
            'id': next_post['id'],
            'posted_date': datetime.now(timezone.utc).isoformat(),
            'bluesky_uri': response.uri
        })
        posted_data['total_posted'] = len(posted_data['log'])
        
        save_json(POSTED_FILE, posted_data)
        print("Updated posted.json")
        
    except Exception as e:
        print(f"Error posting to Bluesky: {e}")
        raise


if __name__ == '__main__':
    main()
```

---

## Content Generation Workflow

### Weekly Process with VS Code Copilot (15-30 minutes)

1. **Open VS Code** in the LoveBot workspace

2. **Open Copilot Chat** (Ctrl+Shift+I or Cmd+Shift+I)

3. **Use the generation prompt** from `prompts/GENERATE_WEEKLY.md`:
   ```
   @workspace Generate 7 LoveBot posts for this week...
   ```

4. **Review the generated content:**
   - Is it aligned with the mission?
   - Is it succinct and clear (under 280 chars)?
   - Does it feel authentic?
   - Edit as needed

5. **Add approved posts to `content/posts.json`**

6. **Commit and push to GitHub**

Copilot will automatically use the instructions in `.github/copilot-instructions.md` to understand the tone, sources, and guidelines.

### Content Guidelines for AI Prompts

When generating content, ensure:
- **Length:** 260 characters max for content (hashtags appended separately)
- **Tone:** Warm, inclusive, hopeful — not preachy
- **Clarity:** Simple language, no jargon
- **Actionable:** When possible, give something to practice
- **Attribution:** Include source when quoting directly
- **Hashtags:** Include 2-3 hashtags per post (see Hashtag Strategy below)

### Hashtag Strategy

Each post includes a `hashtags` array with 2-3 tags. At post time, `post.py` appends them as `\n\n#Tag1 #Tag2 #Tag3`. If the final text would exceed 300 chars, tags are progressively dropped.

**Broad discovery tags** (1 per post, rotating):
`DailyLove`, `SpreadLove`, `LoveReminder`, `DailyInspiration`

**Pillar-specific tags** (1-2 per post):
| Pillar | Tags |
|--------|------|
| self-love | `SelfLove`, `SelfCompassion` |
| care | `Kindness`, `Compassion` |
| responsibility | `LoveInAction`, `ShowUp` |
| respect | `Respect`, `Empathy` |
| trust | `Trust`, `Vulnerability` |
| honesty | `Honesty`, `AuthenticLove` |
| commitment | `Commitment`, `ShowUp` |
| knowledge | `KnowYourself`, `MindfulLove` |

**Content-type tags** (optional): `LoveQuotes`, `DailyPractice`

---

## Character Limits

Bluesky allows **300 characters** per post (graphemes, not bytes).

Content text targets **260 characters** to leave room for hashtags, which are appended automatically at post time from the `hashtags` field. If adding hashtags would exceed 300 characters, they are progressively dropped.

### Good length examples:

**Short (under 150 chars):**
> Love isn't a feeling we fall into. It's a practice we rise to—one choice at a time.

**Medium (150-220 chars):**
> "The purpose of loving is not to have our needs met but to extend ourselves." — M. Scott Peck

> Today's practice: Before reacting, pause and ask—what would love do here?

**Full (220-260 chars):**
> Love requires seven things: care, responsibility, respect, trust, honesty, commitment, and knowledge. Not all at once, but as a practice. Today, choose one.

---

## Timezone Reference

Adjust the cron schedule for your timezone:

| Timezone | 7:00 AM Local | Cron Expression |
|----------|---------------|-----------------|
| UTC | 7:00 AM UTC | `0 7 * * *` |
| US Eastern (EST) | 7:00 AM | `0 12 * * *` |
| US Eastern (EDT) | 7:00 AM | `0 11 * * *` |
| US Pacific (PST) | 7:00 AM | `0 15 * * *` |
| US Pacific (PDT) | 7:00 AM | `0 14 * * *` |
| UK (GMT) | 7:00 AM | `0 7 * * *` |
| UK (BST) | 7:00 AM | `0 6 * * *` |

---

## Testing

### Local Testing
```bash
# Set environment variables
export BLUESKY_HANDLE="lovebotdaily.bsky.social"
export BLUESKY_APP_PASSWORD="your-app-password"

# Run the script
python src/post.py
```

### GitHub Actions Testing
1. Go to Actions tab in your repository
2. Select "Daily Love Post" workflow
3. Click "Run workflow" button
4. Check the logs for any errors

---

## Monitoring & Maintenance

### Weekly Tasks
- [ ] Generate and approve next week's content
- [ ] Check that posts went out successfully
- [ ] Review any engagement/replies on Bluesky

### Monthly Tasks
- [ ] Review content performance (which posts resonated?)
- [ ] Ensure content library has 30+ days of posts queued
- [ ] Update prompts if content quality needs adjustment

### If Something Breaks
1. Check GitHub Actions logs for errors
2. Verify Bluesky app password is still valid
3. Ensure posts.json has unposted content
4. Check Bluesky API status

---

## Future Enhancements (Phase 2+)

Once the basic bot is running well, consider:

- [ ] Add images/quote cards (Canva free tier)
- [ ] Cross-post to Mastodon (also free)
- [ ] Track engagement metrics
- [ ] A/B test different content types
- [ ] Build a simple web dashboard
- [ ] Accept quote submissions from community

---

## Quick Start Checklist

- [ ] Create Bluesky account
- [ ] Create app password on Bluesky
- [ ] Fork/clone this repository
- [ ] Add secrets to GitHub repository
- [ ] Generate first batch of content (7-14 posts)
- [ ] Add content to posts.json
- [ ] Enable GitHub Actions
- [ ] Test with manual workflow trigger
- [ ] Verify post appears on Bluesky
- [ ] Let it run! 🎉

---

## Questions for Programmer Handoff

All technical decisions have been made. A programmer should be able to implement this directly. 

**Estimated development time:** 2-4 hours

**Skills needed:**
- Basic Python
- GitHub/Git
- JSON
- GitHub Actions (or willingness to learn — it's simple)
