"""
LoveBot - Auto content generator

Generates new posts using the GitHub Models API (free, no extra API key needed
in GitHub Actions — uses the built-in GITHUB_TOKEN).

Falls back to standard OpenAI API if OPENAI_API_KEY is set instead.

Usage:
    python src/generate.py                    # Generate 14 posts (if buffer is low)
    python src/generate.py --count 7          # Generate exactly 7 posts
    python src/generate.py --force            # Generate even if buffer is sufficient
    python src/generate.py --dry-run          # Preview prompt without calling API
    python src/generate.py --check            # Exit 1 if generation is needed, 0 if not
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root or src/
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)


# --- Configuration -----------------------------------------------------------

CONTENT_DIR = Path(__file__).parent.parent / "content"
POSTED_FILE = CONTENT_DIR / "posted.json"
INSTRUCTIONS_FILE = Path(__file__).parent.parent / ".github" / "copilot-instructions.md"

GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o-mini"

# Generate a new batch when fewer than this many posts remain unposted.
# 21 = 3 weeks of buffer — keeps the queue comfortable.
LOW_CONTENT_THRESHOLD = 21

# How many posts to generate per batch when triggered automatically.
DEFAULT_COUNT = 14

# Character limits.
# LOVEBOT_TARGET_LIMIT is the project's preferred ceiling (from copilot-instructions.md).
# BLUESKY_HARD_LIMIT is Bluesky's absolute cap — we never want to hit it.
LOVEBOT_TARGET_LIMIT = 280
BLUESKY_HARD_LIMIT = 300
LOVEBOT_TRUNCATE_SUFFIX = "..."

# Pillars cycle — self-love (Sunday theme) + all Seven Pillars of Love.
# Kept as 8 entries so every pillar, including "responsibility", appears in
# generated batches. The cycle does not need to align 1:1 with days of the week.
PILLARS_CYCLE = [
    "self-love",      # Sunday theme (foundation of all love)
    "care",           # Pillar 1
    "responsibility", # Pillar 2
    "respect",        # Pillar 3
    "trust",          # Pillar 4
    "honesty",        # Pillar 5
    "commitment",     # Pillar 6
    "knowledge",      # Pillar 7
]


# --- Data helpers ------------------------------------------------------------

def load_json(filepath: Path) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if "posted" in str(filepath):
            return {"log": [], "total_posted": 0}
        return {"posts": []}
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")
        return {"posts": []}


def load_all_posts() -> list:
    all_posts = []
    for filepath in sorted(glob.glob(str(CONTENT_DIR / "posts-*.json"))):
        data = load_json(Path(filepath))
        all_posts.extend(data.get("posts", []))
    return all_posts


def get_remaining_count(all_posts: list, posted_data: dict) -> int:
    posted_ids = {entry["id"] for entry in posted_data.get("log", [])}
    return sum(
        1 for p in all_posts
        if p["id"] not in posted_ids and not p.get("posted", False)
    )


def get_next_id(all_posts: list) -> int:
    """Return the integer value of the next sequential post ID."""
    ids = []
    for post in all_posts:
        try:
            ids.append(int(post["id"]))
        except (ValueError, TypeError):
            pass
    return (max(ids) + 1) if ids else 1


def load_instructions() -> str:
    try:
        with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_recent_themes(all_posts: list, n: int = 14) -> list[str]:
    """Return short snippets from the most recent posts to help avoid duplication."""
    recent = all_posts[-n:] if len(all_posts) > n else all_posts
    return [p["content"][:80] for p in recent]


# --- Prompt builder ----------------------------------------------------------

def build_prompt(count: int, next_id: int, instructions: str, recent_themes: list[str]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    pillar_list = "\n".join(
        f"  Post {i + 1}: {PILLARS_CYCLE[i % len(PILLARS_CYCLE)]}"
        for i in range(count)
    )
    recent_sample = "\n".join(f'  - "{t}"' for t in recent_themes[:10])

    return f"""You are generating posts for LoveBot, a daily Bluesky bot.

=== BOT GUIDELINES ===
{instructions}

=== YOUR TASK ===
Generate exactly {count} posts as a valid JSON array.
Start IDs at {next_id:03d} and increment by 1 for each post.

=== PILLAR SEQUENCE (follow this order exactly) ===
{pillar_list}

=== RECENTLY USED THEMES (avoid repeating these ideas) ===
{recent_sample}

=== OUTPUT FORMAT ===
Return ONLY a raw JSON array — no markdown fences, no explanation.

[
  {{
    "id": "{next_id:03d}",
    "content": "Post text here, including attribution at the end — Inspired by [Author]",
    "source": "Author name or 'Original'",
    "pillar": "pillar-name",
    "type": "quote | reflection | question | practice",
    "created_date": "{today}",
    "posted": false,
    "posted_date": null
  }},
  ...
]

=== HARD REQUIREMENTS ===
- Each "content" field: {LOVEBOT_TARGET_LIMIT} characters or fewer (project limit; Bluesky's hard cap is {BLUESKY_HARD_LIMIT} — count carefully)
- Attribution must be inside "content" (e.g., "— Inspired by bell hooks" or "— Thich Nhat Hanh")
- Mix types across the batch: use a variety of quote, reflection, question, and practice
- Tone: warm, inclusive, hopeful — never preachy, never guilt-tripping
- Language: simple and accessible, no jargon
- Generate exactly {count} posts with sequential IDs starting at {next_id:03d}
"""


# --- API call ----------------------------------------------------------------

def build_client() -> tuple[OpenAI, str]:
    """
    Build an OpenAI-compatible client.
    Priority:
      1. GITHUB_TOKEN  → GitHub Models (free, works natively in GitHub Actions)
      2. OPENAI_API_KEY → Standard OpenAI API (fallback for local use)
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if github_token:
        return (
            OpenAI(base_url=GITHUB_MODELS_ENDPOINT, api_key=github_token),
            f"GitHub Models ({MODEL_NAME})",
        )
    elif openai_key:
        return (
            OpenAI(api_key=openai_key),
            f"OpenAI API ({MODEL_NAME})",
        )
    else:
        raise ValueError(
            "No AI API credentials found.\n"
            "In GitHub Actions: GITHUB_TOKEN is set automatically.\n"
            "Locally: set GITHUB_TOKEN (GitHub PAT with models:read scope)\n"
            "      or OPENAI_API_KEY (standard OpenAI key)."
        )


def call_api(client: OpenAI, prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a content generator for LoveBot. "
                    "Return only a valid JSON array with no markdown or explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


# --- Post validation ---------------------------------------------------------

def validate_posts(raw_posts: list, next_id: int) -> tuple[list, list]:
    """
    Validate and lightly fix each post.
    Returns (valid_posts, error_messages).
    """
    valid = []
    errors = []
    required_fields = ["id", "content", "source", "pillar", "type", "created_date"]

    for i, post in enumerate(raw_posts):
        # Guard against non-dict items (e.g. null or a bare string from the model)
        if not isinstance(post, dict):
            errors.append(
                f"Post {i + 1}: expected a JSON object, got {type(post).__name__} — skipped"
            )
            continue

        # Check required fields
        missing = [f for f in required_fields if f not in post]
        if missing:
            errors.append(f"Post {i + 1}: missing fields {missing} — skipped")
            continue

        # Fix sequential ID if model drifted
        expected_id = f"{next_id + i:03d}"
        if post["id"] != expected_id:
            errors.append(
                f"Post {i + 1}: ID was '{post['id']}', corrected to '{expected_id}'"
            )
            post["id"] = expected_id

        # Enforce the project's preferred character limit (truncate rather than discard)
        if len(post["content"]) > LOVEBOT_TARGET_LIMIT:
            errors.append(
                f"Post {i + 1} (ID {post['id']}): content was {len(post['content'])} chars, truncated"
            )
            post["content"] = (
                post["content"][: LOVEBOT_TARGET_LIMIT - len(LOVEBOT_TRUNCATE_SUFFIX)]
                + LOVEBOT_TRUNCATE_SUFFIX
            )

        # Ensure boolean/null defaults
        post.setdefault("posted", False)
        post.setdefault("posted_date", None)

        valid.append(post)

    return valid, errors


# --- File I/O ----------------------------------------------------------------

def save_posts(posts: list) -> Path:
    """
    Save posts to content/posts-YYYY-MM-DD.json.
    If a file for today already exists, the new posts are appended to it.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = CONTENT_DIR / f"posts-{today}.json"

    if filepath.exists():
        existing = load_json(filepath)
        all_posts = existing.get("posts", []) + posts
    else:
        all_posts = posts

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"posts": all_posts}, f, indent=2, ensure_ascii=False)

    return filepath


# --- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LoveBot — Auto content generator via GitHub Models"
    )
    parser.add_argument(
        "--count", type=int, default=DEFAULT_COUNT,
        help=f"Number of posts to generate (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Generate even if the content buffer is above the low threshold",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the prompt without calling the API",
    )
    parser.add_argument(
        "--check", action="store_true",
        help=(
            "Check whether generation is needed. "
            "Exits 1 (needs generation) or 0 (buffer is fine)."
        ),
    )
    args = parser.parse_args()

    # Load current state
    all_posts = load_all_posts()
    posted_data = load_json(POSTED_FILE)
    remaining = get_remaining_count(all_posts, posted_data)
    next_id = get_next_id(all_posts)

    print(f"📊 Content status: {remaining} posts remaining unposted")

    # --check mode: just report and exit
    if args.check:
        if remaining < LOW_CONTENT_THRESHOLD:
            print(f"⚠️  Below threshold ({LOW_CONTENT_THRESHOLD}). Generation needed.")
            sys.exit(1)
        else:
            print(f"✅ Buffer is sufficient ({remaining} ≥ {LOW_CONTENT_THRESHOLD}). No action needed.")
            sys.exit(0)

    # Skip generation if buffer is healthy (unless --force)
    if remaining >= LOW_CONTENT_THRESHOLD and not args.force:
        print(
            f"✅ Buffer is sufficient ({remaining} posts, threshold is {LOW_CONTENT_THRESHOLD}).\n"
            "   Use --force to generate anyway."
        )
        return

    print(f"🔢 Next post ID: {next_id:03d}")
    print(f"📝 Generating {args.count} posts...")

    instructions = load_instructions()
    recent_themes = get_recent_themes(all_posts)
    prompt = build_prompt(args.count, next_id, instructions, recent_themes)

    # Dry run: show prompt and exit
    if args.dry_run:
        print("\n🔍 DRY RUN — prompt that would be sent to the API:\n")
        print("-" * 60)
        print(prompt)
        print("-" * 60)
        return

    # Call the API
    try:
        client, label = build_client()
        print(f"🤖 Calling {label}...")
        raw_text = call_api(client, prompt)
    except ValueError as e:
        print(f"\n❌ Credential error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ API error: {e}")
        sys.exit(1)

    # Parse JSON
    try:
        # Strip markdown fences if model wrapped the output
        clean = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
        clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE).strip()
        raw_posts = json.loads(clean)
        if not isinstance(raw_posts, list):
            raise ValueError(f"Expected a JSON array, got {type(raw_posts).__name__}")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\n❌ Could not parse API response as JSON: {e}")
        print("\nRaw response:\n", raw_text[:500])
        sys.exit(1)

    # Validate
    valid_posts, issues = validate_posts(raw_posts, next_id)

    if issues:
        print(f"\n⚠️  {len(issues)} validation note(s):")
        for msg in issues:
            print(f"   • {msg}")

    if not valid_posts:
        print("\n❌ No valid posts in the API response. Nothing saved.")
        sys.exit(1)

    # Save
    filepath = save_posts(valid_posts)

    print(f"\n✅ Generated {len(valid_posts)} post(s)")
    print(f"   Saved to: {filepath.name}")
    print(f"\n📋 Preview (first 3):")
    for post in valid_posts[:3]:
        chars = len(post["content"])
        print(f"\n   [{post['id']}] {post['pillar']} / {post['type']} ({chars} chars)")
        preview = post["content"].replace("\n", " ")[:100]
        print(f"   {preview}{'...' if len(post['content']) > 100 else ''}")
    if len(valid_posts) > 3:
        print(f"\n   … and {len(valid_posts) - 3} more post(s)")


if __name__ == "__main__":
    main()
