# LoveBot Content Generation Prompts

These prompts are for reference. For weekly content generation, use **`GENERATE_WEEKLY.md`** with VS Code Copilot.

---

## How Content Generation Works

1. **VS Code Copilot** reads `.github/copilot-instructions.md` automatically
2. Open Copilot Chat and use `@workspace` prefix
3. Copilot generates posts following LoveBot's tone and guidelines
4. You review, edit, and approve before adding to `posts.json`

See `GENERATE_WEEKLY.md` for the step-by-step workflow.

---

## Master Prompt (Reference)

```
You are a content creator for a social media account called LoveBot. The mission is to help people understand what love truly is and inspire them to practice it daily.

**Core definition of love:**
"Love is the will to extend one's self for the purposes of nurturing and nourishing one's own or another's spiritual growth." — M. Scott Peck

**The seven pillars of love:**
1. Care — Active concern for the life and growth of another
2. Responsibility — Responding to the needs of another
3. Respect — Seeing others as they truly are, not as we wish them to be
4. Trust — Believing in the reliability of another
5. Honesty — Sharing one's true self with compassion
6. Commitment — Showing up consistently over time
7. Knowledge — Truly knowing oneself and others

**Source inspiration:**
Draw wisdom from these authors and works:
- bell hooks — "All About Love"
- M. Scott Peck — "The Road Less Traveled"
- Byron Katie — "Loving What Is"
- Fred Rogers (Mister Rogers)
- Marshall Rosenberg — "Nonviolent Communication"
- John Bradshaw — "Creating Love"
- Marianne Williamson — "A Return to Love"
- Carl Sagan — His writings on humanity and connection
- Thich Nhat Hanh — "How to Love"
- Erich Fromm — "The Art of Loving"

**Content guidelines:**
- Maximum 280 characters (strict limit)
- Warm, inclusive, hopeful tone
- Never preachy or judgmental
- Simple, clear language
- When quoting directly, include brief attribution
- Mix of: quotes, reflections, questions, and daily practices
- Aim to inspire self-love AND love for others

**Generate 7 posts**, one for each day of the week, following this theme rotation:
- Sunday: Self-Love
- Monday: Care
- Tuesday: Trust
- Wednesday: Honesty
- Thursday: Respect
- Friday: Commitment
- Saturday: Knowledge

For each post, provide:
1. The post text (under 280 characters)
2. The pillar/theme
3. The content type (quote/reflection/question/practice)
4. Source inspiration (which author/work inspired it)
```

---

## Variation Prompts

### For Quote-Heavy Week
```
Generate 7 short quotes (under 280 characters each) about love from or inspired by bell hooks, M. Scott Peck, Mister Rogers, and Thich Nhat Hanh. Include attribution. Focus on love as action, not just feeling.
```

### For Practice-Focused Week
```
Generate 7 brief daily love practices (under 280 characters each). Each should give the reader something small but meaningful they can do TODAY to practice love—either self-love or love for others. Make them specific and actionable.
```

### For Question/Reflection Week
```
Generate 7 reflective questions about love (under 280 characters each). These should prompt self-examination without being intrusive. Focus on the seven pillars: care, responsibility, respect, trust, honesty, commitment, knowledge.
```

### For Self-Love Focus
```
Generate 7 posts about self-love (under 280 characters each). Draw from bell hooks' idea that we cannot give love we don't have for ourselves. Include a mix of quotes, affirmations, and practices. Warm and encouraging tone.
```

### For Combating Narcissism/Greed Theme
```
Generate 7 posts (under 280 characters each) that gently contrast love with its opposites—greed, narcissism, exploitation—without being negative or preachy. Focus on what love IS rather than attacking what it isn't. Inspire the reader toward connection over consumption.
```

---

## Sample Output Format

When the AI generates content, ask it to format like this for easy copying to posts.json:

```json
{
  "id": "XXX",
  "content": "THE POST TEXT HERE",
  "source": "Inspired by bell hooks",
  "pillar": "care",
  "type": "reflection",
  "created_date": "2026-02-21",
  "posted": false,
  "posted_date": null
}
```

---

## Quality Checklist

Before adding generated content to posts.json, verify each post:

- [ ] Under 280 characters?
- [ ] Clear and easy to understand?
- [ ] Warm, not preachy?
- [ ] Aligned with the mission?
- [ ] Would you want to read this?
- [ ] Attribution included if it's a direct quote?
- [ ] Unique ID assigned?

---

## Example Generated Posts

### Quotes
```
"To begin by always thinking of love as an action rather than a feeling is one way in which anyone using the word in this manner automatically assumes accountability." — bell hooks
```
(278 characters)

```
"Love is an act of will—both an intention and an action." — M. Scott Peck

Today, let love be your verb.
```
(103 characters)

### Reflections
```
You cannot pour from an empty cup. Self-love isn't selfish—it's the foundation that makes all other love possible.
```
(113 characters)

```
Love asks us to be curious instead of certain. To listen instead of fix. To witness instead of judge.
```
(101 characters)

### Questions
```
What's one small way you can show yourself care today? Not earned. Not conditional. Just because you exist.
```
(107 characters)

```
Who in your life needs to be truly seen today? What would it mean to offer them your full attention?
```
(100 characters)

### Practices
```
Today's practice: When someone speaks, listen fully. Don't plan your response. Just be present. That's love in action.
```
(118 characters)

```
Before bed tonight, name three things you appreciate about yourself. Not what you did—who you are.
```
(98 characters)

---

## Keeping Content Fresh

Every few weeks, try these variations:
- Focus on a single author for a week
- Theme around a current season or holiday
- Address common struggles (loneliness, self-criticism, conflict)
- Celebrate love in unexpected places (strangers, nature, community)

Remember: The goal is consistency over perfection. A simple, heartfelt post every day beats an elaborate post that never goes out.
