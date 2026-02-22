"""
LoveBot - Daily Bluesky poster
Posts one piece of content about love each day.

Usage:
    python src/post.py           # Post the next unposted content
    python src/post.py --dry-run # Preview without posting
    python src/post.py --status  # Check content library status
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports when running from src/
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from atproto import Client
except ImportError:
    print("Error: atproto not installed. Run: pip install atproto")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional - credentials can come from environment
    pass


# Configuration
CONTENT_DIR = Path(__file__).parent.parent / 'content'
POSTED_FILE = CONTENT_DIR / 'posted.json'


def load_json(filepath: Path) -> dict:
    """Load JSON file, return empty structure if not exists."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        if 'posted' in str(filepath):
            return {"log": [], "total_posted": 0}
        return {"posts": []}
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")
        return {"posts": []} if 'posted' not in str(filepath) else {"log": [], "total_posted": 0}


def load_all_posts() -> list:
    """Load posts from all posts-*.json files in content directory."""
    all_posts = []
    pattern = str(CONTENT_DIR / 'posts-*.json')
    
    for filepath in sorted(glob.glob(pattern)):
        data = load_json(Path(filepath))
        posts = data.get('posts', [])
        # Add source file info for debugging
        for post in posts:
            post['_source_file'] = os.path.basename(filepath)
        all_posts.extend(posts)
    
    return all_posts


def save_json(filepath: Path, data: dict) -> None:
    """Save data to JSON file."""
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_post(all_posts: list, posted_data: dict) -> dict | None:
    """Get the next unposted content."""
    posted_ids = {entry['id'] for entry in posted_data.get('log', [])}
    
    for post in all_posts:
        if post['id'] not in posted_ids and not post.get('posted', False):
            return post
    
    return None


def get_bluesky_credentials() -> tuple[str, str]:
    """Get Bluesky credentials from environment variables."""
    handle = os.environ.get('BLUESKY_HANDLE')
    password = os.environ.get('BLUESKY_APP_PASSWORD')
    
    if not handle:
        raise ValueError(
            "Missing BLUESKY_HANDLE environment variable.\n"
            "Set it in .env file or as a GitHub Secret."
        )
    
    if not password:
        raise ValueError(
            "Missing BLUESKY_APP_PASSWORD environment variable.\n"
            "Create an app password at: https://bsky.app/settings/app-passwords\n"
            "Then set it in .env file or as a GitHub Secret."
        )
    
    return handle, password


def post_to_bluesky(content: str) -> dict:
    """Post content to Bluesky and return the response."""
    handle, password = get_bluesky_credentials()
    
    client = Client()
    client.login(handle, password)
    
    # Validate content length (Bluesky limit is 300 graphemes)
    if len(content) > 300:
        print(f"Warning: Content is {len(content)} characters, truncating to 300")
        content = content[:297] + "..."
    
    response = client.send_post(text=content)
    return response


def update_posted_log(posted_data: dict, post: dict, bluesky_uri: str) -> dict:
    """Update the posted.json log with the new post."""
    posted_data['log'].append({
        'id': post['id'],
        'posted_date': datetime.now(timezone.utc).isoformat(),
        'bluesky_uri': bluesky_uri,
        'pillar': post.get('pillar', ''),
        'type': post.get('type', ''),
        'source_file': post.get('_source_file', '')
    })
    posted_data['total_posted'] = len(posted_data['log'])
    
    return posted_data


def print_status(all_posts: list, posted_data: dict) -> None:
    """Print content library status."""
    posted_ids = {entry['id'] for entry in posted_data.get('log', [])}
    unposted = [p for p in all_posts if p['id'] not in posted_ids and not p.get('posted', False)]
    
    print("\n📊 LoveBot Content Status")
    print("=" * 40)
    print(f"Total posts in library: {len(all_posts)}")
    print(f"Already posted: {len(posted_ids)}")
    print(f"Remaining: {len(unposted)}")
    print(f"Days of content left: {len(unposted)}")
    
    if len(unposted) < 7:
        print("\n⚠️  Warning: Less than 1 week of content remaining!")
        print("Run content generation to add more posts.")
    
    if unposted:
        print(f"\nNext post (ID {unposted[0]['id']}):")
        print(f"  Pillar: {unposted[0].get('pillar', 'N/A')}")
        print(f"  Type: {unposted[0].get('type', 'N/A')}")
        print(f"  Preview: {unposted[0]['content'][:80]}...")


def main():
    """Main function to post daily content."""
    parser = argparse.ArgumentParser(description='LoveBot - Daily Bluesky poster')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview the post without actually posting')
    parser.add_argument('--status', action='store_true',
                        help='Show content library status')
    args = parser.parse_args()
    
    # Load data
    all_posts = load_all_posts()
    posted_data = load_json(POSTED_FILE)
    
    print(f"📚 Loaded {len(all_posts)} total posts from content/posts-*.json files")
    
    # Status mode
    if args.status:
        print_status(all_posts, posted_data)
        return
    
    # Get next post
    next_post = get_next_post(all_posts, posted_data)
    
    if not next_post:
        print("❌ No unposted content available!")
        print("   Add more posts to content/posts-YYYY-MM-DD.json")
        sys.exit(1)
    
    print(f"\n📝 Next post (ID: {next_post['id']})")
    print(f"   Pillar: {next_post.get('pillar', 'N/A')}")
    print(f"   Type: {next_post.get('type', 'N/A')}")
    print(f"   Characters: {len(next_post['content'])}")
    print(f"\n   Content:\n   {'-' * 40}")
    # Print content with indentation
    for line in next_post['content'].split('\n'):
        print(f"   {line}")
    print(f"   {'-' * 40}")
    
    # Dry run mode
    if args.dry_run:
        print("\n🔍 DRY RUN - Not posting to Bluesky")
        return
    
    # Post to Bluesky
    try:
        print("\n🚀 Posting to Bluesky...")
        response = post_to_bluesky(next_post['content'])
        print(f"✅ Successfully posted!")
        print(f"   URI: {response.uri}")
        
        # Update posted.json
        posted_data = update_posted_log(posted_data, next_post, response.uri)
        save_json(POSTED_FILE, posted_data)
        print(f"📋 Updated posted.json (total: {posted_data['total_posted']})")
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error posting to Bluesky: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
