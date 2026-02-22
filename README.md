# LoveBot 💙

A daily Bluesky bot that shares wisdom about love — what it truly is and how to practice it.

**Handle:** [@lovebotdaily.bsky.social](https://bsky.app/profile/lovebotdaily.bsky.social)

## Mission

Help people understand what love truly is and inspire them to practice it daily.

> "Love is the will to extend one's self for the purposes of nurturing and nourishing one's own or another's spiritual growth." — M. Scott Peck

## The Seven Pillars of Love

1. **Care** — Active concern for the life and growth of another
2. **Responsibility** — Responding to the needs of another
3. **Respect** — Seeing others as they truly are
4. **Trust** — Believing in the reliability of another
5. **Honesty** — Sharing one's true self with compassion
6. **Commitment** — Showing up consistently over time
7. **Knowledge** — Truly knowing oneself and others

## Source Materials

Wisdom drawn from:
- bell hooks — *All About Love*
- M. Scott Peck — *The Road Less Traveled*
- Byron Katie — *Loving What Is*
- Fred Rogers
- Marshall Rosenberg — *Nonviolent Communication*
- John Bradshaw — *Creating Love*
- Marianne Williamson — *A Return to Love*
- Thich Nhat Hanh — *How to Love*
- Erich Fromm — *The Art of Loving*

## How It Works

- Posts once daily at 6:00 AM PST
- Content is AI-assisted (VS Code Copilot) and human-approved
- Runs automatically via GitHub Actions (free!)
- No server needed

## Project Structure

```
LoveBot/
├── .github/
│   ├── copilot-instructions.md   # AI context for content generation
│   └── workflows/
│       └── daily-post.yml        # Automated daily posting
├── content/
│   ├── posts-YYYY-MM-DD.json     # Approved posts (dated batches)
│   └── posted.json               # Log of what's been posted
├── src/
│   └── post.py                   # Posting script
├── prompts/
│   └── GENERATE_WEEKLY.md        # Weekly content generation workflow
└── requirements.txt
```

## Local Development

### Setup

```bash
# Clone the repo
git clone https://github.com/jenfoxbot/lovebot.git
cd lovebot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up credentials
cp .env.example .env
# Edit .env with your Bluesky app password
```

### Commands

```bash
# Check content status
python src/post.py --status

# Preview next post (without posting)
python src/post.py --dry-run

# Post to Bluesky
python src/post.py
```

## Adding Content

1. Open VS Code with this workspace
2. Open Copilot Chat and use the prompt from `prompts/GENERATE_WEEKLY.md`
3. Review and edit the generated posts
4. Save to `content/posts-YYYY-MM-DD.json`
5. Commit and push

## License

Content is shared with love. 💙
