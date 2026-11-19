#!/usr/bin/env python3
"""Read-only World's Edge alias lookup for JI roster names.

Queries both the configured display tag and a conservative clan-prefix-free
candidate. Results are diagnostic only: this script never edits config or data.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ratings import STATS_URL, HEADERS

CONFIG = ROOT / "config" / "players.json"
BATCH_SIZE = 10


def alias_candidates(tag):
    """Return the exact configured tag and a possible bare in-game name."""
    tag = " ".join((tag or "").split())
    candidates = [tag] if tag else []
    bare = re.sub(r"^\[JAGR\]\s*", "", tag, flags=re.IGNORECASE)
    bare = re.sub(r"^JAGR\s*(?:\|\s*|I\s+|_)?", "", bare, flags=re.IGNORECASE)
    bare = bare.strip()
    if bare and bare not in candidates:
        candidates.append(bare)
    return candidates


def request_aliases(aliases):
    query = urlencode({"title": "age2", "aliases": json.dumps(aliases)})
    req = Request(f"{STATS_URL}?{query}", headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("result", {}).get("code") != 0:
        raise ValueError(f"API error: {data.get('result')}")
    return data


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    players = config["players"]
    owners = {}
    for player in players:
        for alias in alias_candidates(player.get("tag", "")):
            owners.setdefault(alias, []).append(player)

    aliases = list(owners)
    print(f"Roster: {config.get('clan_name', 'unknown')} — {len(players)} players")
    print(f"Unique alias candidates: {len(aliases)}")
    print("Candidates include configured tags and possible names without the JAGR prefix.")
    print("No roster/config/data files are modified. Review identity matches before adding official_id.")

    for start in range(0, len(aliases), BATCH_SIZE):
        batch = aliases[start:start + BATCH_SIZE]
        print(f"\n=== alias lookup {start + 1}-{start + len(batch)} ===")
        data = request_aliases(batch)
        profiles = data.get("profiles", [])
        by_alias = {}
        for profile in profiles:
            by_alias.setdefault(profile.get("alias"), []).append(profile)

        for alias in batch:
            matches = by_alias.get(alias, [])
            linked_players = [
                {"tag": p.get("tag"), "aoe2insights_id": p.get("id")}
                for p in owners[alias]
            ]
            if not matches:
                print(json.dumps({
                    "queried_alias": alias,
                    "roster_players": linked_players,
                    "status": "NO_EXACT_MATCH",
                }, ensure_ascii=False))
                continue
            for profile in matches:
                print(json.dumps({
                    "queried_alias": alias,
                    "roster_players": linked_players,
                    "status": "MATCH",
                    "official_profile_id": profile.get("profile_id"),
                    "returned_alias": profile.get("alias"),
                    "name": profile.get("name"),
                    "personal_statgroup_id": profile.get("personal_statgroup_id"),
                }, ensure_ascii=False))


if __name__ == "__main__":
    main()
