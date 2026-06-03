#!/usr/bin/env python3
"""Filter LinkedIn candidate posts to only those not seen in prior runs.

Input: JSON array of post objects via --input or stdin.
Each post should include a stable `url`; if neither URL nor ID exists, a hash of
account/source/created_at/title/text is used.
Output: JSON array of new posts. Updates the seen-posts state by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def default_state_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(codex_home) / "skills" / "linkedin-account-digest" / "state" / "seen-posts.json"


def load_posts(input_path: str | None) -> list[dict[str, Any]]:
    if input_path:
        raw = Path(input_path).read_text(encoding="utf-8")
    else:
        import sys

        raw = sys.stdin.read()
    data = json.loads(raw or "[]")
    if not isinstance(data, list):
        raise SystemExit("Input must be a JSON array of post objects")
    return [p for p in data if isinstance(p, dict)]


def post_key(post: dict[str, Any]) -> str:
    for field in ("url", "post_url", "id", "post_id", "urn"):
        value = post.get(field)
        if value:
            return str(value)
    basis = "|".join(
        str(post.get(k, ""))
        for k in ("account", "source_url", "created_at", "published_at", "title", "text")
    )
    return "sha256:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()


def load_seen(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8") or "[]")
    if isinstance(data, list):
        return {str(x) for x in data}
    if isinstance(data, dict):
        return {str(x) for x in data.get("seen", [])}
    return set()


def save_seen(path: Path, seen: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seen": sorted(seen)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON file containing a list of posts")
    parser.add_argument("--state", default=str(default_state_path()), help="State file path")
    parser.add_argument("--no-update", action="store_true", help="Print new posts without updating state")
    args = parser.parse_args()

    state_path = Path(args.state)
    posts = load_posts(args.input)
    seen = load_seen(state_path)

    new_posts: list[dict[str, Any]] = []
    for post in posts:
        key = post_key(post)
        if key in seen:
            continue
        enriched = dict(post)
        enriched.setdefault("_dedupe_key", key)
        new_posts.append(enriched)
        seen.add(key)

    if not args.no_update:
        save_seen(state_path, seen)

    print(json.dumps(new_posts, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
