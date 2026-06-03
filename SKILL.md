---
name: linkedin-account-digest
description: Monitor selected LinkedIn profiles and company post pages, detect public posts not seen in prior runs, and prepare or send an email digest. Use when the user asks to follow LinkedIn accounts, summarize new LinkedIn posts, monitor LinkedIn profiles or company pages, or email a LinkedIn account update.
---

# LinkedIn Account Digest

## Overview

Use this skill to check a fixed watchlist of LinkedIn profile and company post URLs, identify public posts that are new since the previous run, and produce a concise email-ready digest. LinkedIn's API access for arbitrary third-party profiles is limited, so prefer public page/search retrieval for monitored accounts and use LinkedIn API tools only for authenticated self/account operations or known post identifiers.

## Watchlist

Read `references/accounts.md` for the canonical monitored LinkedIn URLs.

Default targets:

- Merve Noyan profile
- Roboflow company posts
- Piotr Skalski profile

## Workflow

1. Determine the check window.
   - For a scheduled daily run, use the user's local day in Asia/Taipei unless the prompt gives another timezone.
   - For an ad hoc run, use the last 24 hours unless the user asks for another range.

2. Fetch public account and post data.
   - Use Composio `COMPOSIO_SEARCH_TOOLS` first for the current workflow.
   - Prefer `COMPOSIO_SEARCH_WEB` to discover recent public post/activity URLs for each target.
   - Use `COMPOSIO_SEARCH_FETCH_URL_CONTENT` to fetch profile/company pages and discovered post permalinks.
   - If static fetch is gated, stale, or dominated by sign-in boilerplate, use Browser Tool as a best-effort fallback.
   - Do not claim completeness when LinkedIn blocks public pages or search results appear cached/stale.

3. Normalize candidate posts into JSON objects and run `scripts/filter_new_posts.py`.
   - Include at minimum `account`, `source_url`, `url`, `created_at` when available, `title`, and `text`.
   - Use stable post URLs as the primary dedupe key.
   - If a stable URL is unavailable, use a hash of account/source/time/title/text.
   - The script stores state under `%CODEX_HOME%/skills/linkedin-account-digest/state/seen-posts.json` by default.

4. Prepare the digest only if there are new posts.
   - Group by account.
   - For each post, include post time if available, direct URL, Traditional Chinese summary, and English summary.
   - Keep summaries factual and label cached/public-search limitations when relevant.
   - If no new posts are found, do not send an email unless the user explicitly asks for no-news notifications.

5. Send or draft email.
   - Use an active Gmail connector or Composio `GMAIL_SEND_EMAIL` when available.
   - If Gmail is unavailable, produce an email-ready subject and body instead.
   - For this user's default workflow, send to `situn50627@gmail.com` only when automatic sending is explicitly requested or already configured by an automation.
   - Suggested subject: `LinkedIn Digest / LinkedIn account post digest - YYYY-MM-DD`.

6. Failure handling.
   - If LinkedIn/public search retrieval fails for every target, send a short bilingual failure report if Gmail is available.
   - If only some targets fail, include those failures under `Notes`.
   - If Gmail send fails, report the failure and preserve fetched post state only if a digest was successfully sent or the user explicitly approves marking posts as seen.

## Email Format

Use this structure:

```text
Subject: LinkedIn Digest / LinkedIn account post digest - YYYY-MM-DD

New posts found: <count>
Accounts checked: Merve Noyan, Roboflow, Piotr Skalski

Merve Noyan
- <time or "time unavailable"> - <short topic>
  Traditional Chinese summary: <1-3 concise Traditional Chinese bullets or sentences>
  English summary: <1-3 concise English bullets or sentences>
  Link: <url>

...

Notes
- Mention targets with lookup/post-fetch failures.
- Mention when data came from public search/cache rather than LinkedIn API.
```

## Safety And Accuracy

- Treat LinkedIn automation as sensitive: do not connect, follow, message, endorse, react, comment, or post from this skill unless the user explicitly asks.
- Do not scrape private or login-only data.
- Prefer direct LinkedIn post URLs when available.
- Preserve the state file; it prevents duplicate daily emails.
