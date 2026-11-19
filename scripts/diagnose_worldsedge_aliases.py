#!/usr/bin/env python3
"""Read-only, one-request-per-player World's Edge alias lookup diagnostic.

Uses each configured in-game tag exactly as written. It prints the complete
JSON response (compactly) so we can inspect the API's actual response shape.
No roster/config/data files are modified.
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ratings import STATS_URL, HEADERS

CONFIG = ROOT / "config" / "players.json"
PAUSE_SECONDS = 0.5


def request_alias(alias):
    # Deliberately send one exact in-game tag per request, not a batch.
    query = urlencode({"title": "age2", "aliases": json.dumps([alias])})
    url = f"{STATS_URL}?{query}"
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        status = resp.status
        raw = resp.read().decode("utf-8")
    return status, url, json.loads(raw), raw


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    players = config["players"]
    print(f"Roster: {config.get('clan_name', 'unknown')} — {len(players)} players")
    print("Mode: one API request per configured tag; exact spelling preserved.")
    print("No roster/config/data files are modified.")
    print(f"Endpoint: {STATS_URL}")

    for index, player in enumerate(players, start=1):
        tag = player.get("tag", "")
        print(f"\n=== PLAYER {index}/{len(players)} ===")
        print(json.dumps({
            "roster_tag": tag,
            "aoe2insights_id": player.get("id"),
            "configured_official_id": player.get("official_id", "(not set; defaults to id)"),
            "member_status": player.get("member_status", "active"),
        }, ensure_ascii=False))
        try:
            status, url, data, raw = request_alias(tag)
            print(f"HTTP_STATUS: {status}")
            print(f"TOP_LEVEL_KEYS: {json.dumps(list(data.keys()), ensure_ascii=False)}")
            print(f"API_RESULT: {json.dumps(data.get('result'), ensure_ascii=False)}")
            profiles = data.get("profiles")
            print(f"PROFILES_TYPE: {type(profiles).__name__}")
            print(f"PROFILES: {json.dumps(profiles, ensure_ascii=False, separators=(',', ':'))}")
            groups = data.get("statGroups")
            group_summary = []
            for group in groups or []:
                group_summary.append({
                    "id": group.get("id"),
                    "members": group.get("members"),
                })
            print(f"STATGROUPS: {json.dumps(group_summary, ensure_ascii=False, separators=(',', ':'))}")
            stats = data.get("leaderboardStats")
            print(f"LEADERBOARD_STATS_COUNT: {len(stats) if isinstance(stats, list) else 'not-a-list-or-missing'}")
            print(f"LEADERBOARD_STATS: {json.dumps(stats, ensure_ascii=False, separators=(',', ':'))}")
            # Preserve the raw response for fields not anticipated by this script.
            print(f"RAW_RESPONSE: {raw}")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"HTTP_ERROR: {exc.code} {exc.reason}")
            print(f"HTTP_ERROR_BODY: {body}")
        except (URLError, TimeoutError, ValueError) as exc:
            print(f"REQUEST_ERROR: {type(exc).__name__}: {exc}")
        if index < len(players):
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
