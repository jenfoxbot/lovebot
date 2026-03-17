# Generate Weekly LoveBot Content

Use this prompt with VS Code Copilot to generate your weekly batch of posts.

## How to Use

1. Open this file in VS Code
2. Open Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I)
3. Type `@workspace` then paste one of the prompts below
4. Review the generated posts
5. Copy approved posts to `content/posts.json`

---

## Weekly Generation Prompt

Copy and paste this into Copilot Chat:

```
@workspace Generate 7 LoveBot posts for this week. Follow the guidelines in .github/copilot-instructions.md. 

Create one post for each day:
- Sunday: Self-Love
- Monday: Care  
- Tuesday: Trust
- Wednesday: Honesty
- Thursday: Respect
- Friday: Commitment
- Saturday: Knowledge

For each post, output valid JSON in this exact format:

{
  "id": "[3-digit number starting after the last ID in posts-*.json files]",
  "content": "[post text with attribution at the end, max 260 characters total]",
  "source": "[author or 'Original']",
  "pillar": "[pillar name]",
  "type": "[quote/reflection/question/practice]",
  "hashtags": ["BroadTag", "PillarTag1", "PillarTag2"],
  "created_date": "[today's date YYYY-MM-DD]",
  "posted": false,
  "posted_date": null
}

IMPORTANT: The "content" field should include the source attribution at the end (e.g., "— Inspired by bell hooks" or "— Fred Rogers") because this is exactly what gets posted to Bluesky. Keep the total under 260 characters including the attribution. Hashtags are appended separately at post time.

HASHTAGS: Each post needs a "hashtags" array with 2-3 tags (no # symbol):
- 1 broad discovery tag (rotate): DailyLove, SpreadLove, LoveReminder, DailyInspiration
- 1-2 pillar tags: SelfLove, SelfCompassion, Kindness, Compassion, LoveInAction, ShowUp, Respect, Empathy, Trust, Vulnerability, Honesty, AuthenticLove, Commitment, KnowYourself, MindfulLove
- Optional: LoveQuotes (for quotes), DailyPractice (for practices)

Make each post unique, varied in type (mix quotes, reflections, questions, practices). Check the existing posts-*.json files to avoid duplicating themes or phrasing.
```

---

## Alternative Prompts

### Quote-Heavy Week
```
@workspace Generate 7 LoveBot posts that are primarily direct quotes. Follow .github/copilot-instructions.md. Include quotes from bell hooks, M. Scott Peck, Fred Rogers, and Thich Nhat Hanh. Each under 260 characters with attribution. Include 2-3 hashtags per post. Output as JSON array matching the posts.json format.
```

### Practice-Focused Week  
```
@workspace Generate 7 LoveBot posts that are all actionable daily practices. Follow .github/copilot-instructions.md. Each should give readers something small but meaningful to DO today to practice love. Under 260 characters each. Include 2-3 hashtags per post. Output as JSON matching posts.json format.
```

### Self-Love Focus
```
@workspace Generate 7 LoveBot posts focused entirely on self-love and self-compassion. Follow .github/copilot-instructions.md. Draw from bell hooks' teaching that we cannot give love we don't have for ourselves. Mix of affirmations, practices, and reflections. Under 260 characters. Include 2-3 hashtags. JSON format.
```

### Question/Reflection Week
```
@workspace Generate 7 reflective questions about love for LoveBot. Follow .github/copilot-instructions.md. Each question should prompt gentle self-examination without being intrusive. Cover all seven pillars across the week. Under 260 characters. Include 2-3 hashtags. JSON format.
```

---

## After Generation

1. **Review each post:**
   - Is it under 260 characters?
   - Does it feel authentic and warm?
   - Is it clear and accessible?
   - Would YOU want to read this?
   - Does it have 2-3 relevant hashtags?

2. **Edit as needed** — AI output is a starting point

3. **Add to posts.json:**
   - Open `content/posts.json`
   - Add the new posts to the `"posts"` array
   - Make sure IDs are sequential and unique

4. **Commit and push:**
   ```
   git add content/posts-YYYY-MM-DD.json
   git commit -m "Add posts for week of [DATE]"
   git push
   ```

---

## Quick ID Reference

Before generating, check the last ID across all `content/posts-*.json` files and tell Copilot to start from the next number.

Example: If last ID is "014", say "Start IDs from 015"
