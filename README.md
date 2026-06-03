# LinkedIn Account Digest Skill

Codex skill for monitoring selected public LinkedIn profiles and company post pages, filtering unseen posts, and generating bilingual email digests.

## What It Monitors

The default watchlist is stored in `references/accounts.md`:

- Merve Noyan: `https://www.linkedin.com/in/merve-noyan-28b1a113a/`
- Roboflow company posts: `https://www.linkedin.com/company/roboflow-ai/posts/?feedView=all`
- Piotr Skalski: `https://www.linkedin.com/in/skalskip92/`

## What It Does

- Finds recent public LinkedIn posts or article URLs for the monitored accounts.
- Fetches public/cached LinkedIn page content with Composio Search or Browser Tool.
- Normalizes candidate posts and filters out previously seen items.
- Produces a bilingual digest with:
  - account name
  - post time when available
  - Traditional Chinese summary
  - English summary
  - direct original URL
- Suppresses email when no new posts are found.
- Sends a short bilingual failure report when retrieval or email delivery fails.

## Files

- `SKILL.md` - Codex skill instructions and workflow.
- `references/accounts.md` - canonical LinkedIn watchlist.
- `scripts/filter_new_posts.py` - deterministic post dedupe helper.
- `agents/openai.yaml` - Codex UI metadata.

## Usage

After installing this folder under your Codex skills directory, restart Codex and ask:

```text
Use $linkedin-account-digest to check monitored LinkedIn accounts and prepare today's email digest.
```

For scheduled delivery, use a Codex automation. Recommended behavior:

- schedule: daily at 09:00 in your local timezone
- recipient: configure privately in the automation prompt, not in this repository
- behavior: send only when new posts are found

## State

The dedupe script stores seen post keys at:

```text
%CODEX_HOME%/skills/linkedin-account-digest/state/seen-posts.json
```

Do not commit the runtime `state/` directory unless you intentionally want to share seen-post history.

## Security Notes

Do not commit private recipient addresses, API keys, OAuth tokens, cookies, account IDs, or runtime state. Keep credentials in Codex connector configuration, Composio connection settings, or local automation prompts.

## Limitations

LinkedIn does not expose complete third-party feeds through the current MCP tool surface. This skill uses public web/search-visible content and should label cached or incomplete data as best-effort.
