#!/usr/bin/env python3
"""Read-only identity diagnostics for the three unresolved JI accounts."""
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ratings import STATS_URL, HEADERS

TARGETS = {
    "JAGR | TheButterfly_Effect": {
        "aoe2insights_id": 12950375,
        "aliases": [
            "JAGR | TheButterfly_Effect",
            "TheButterfly_Effect",
            "JAGR TheButterfly_Effect",
            "TheButterfly Effect",
        ],
    },
    "JAGR | Themoeplay": {
        "aoe2insights_id": 761809,
        "aliases": [
            "JAGR | Themoeplay",
            "JAGR | TheMoePlay",
            "Themoeplay",
            "TheMoePlay",
            "AirNic",
        ],
    },
    "JAGR | Kriid": {
        "aoe2insights_id": 2861536,
        "aliases": [
            "JAGR | Kriid",
            "Kriid",
            "KRIID",
        ],
    },
}

def request_stats(param, values):
    query = urlencode({"title": "age2", param: json.dumps(values)})
    req = Request(f"{STATS_URL}?{query}", headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def summarize(data):
    profiles = data.get("profiles")
    groups = data.get("statGroups")
    stats = data.get("leaderboardStats")
    members = []
    for group in groups or []:
        for member in group.get("members") or []:
            members.append({
                "profile_id": member.get("profile_id"),
                "alias": member.get("alias"),
                "name": member.get("name"),
                "personal_statgroup_id": member.get("personal_statgroup_id"),
            })
    ratings = []
    for stat in stats or []:
        if stat.get("leaderboard_id") == 3:
            ratings.append({
                "leaderboard_id": stat.get("leaderboard_id"),
                "rating": stat.get("rating"),
                "highest_rating": stat.get("highest_rating"),
            })
    return {
        "result": data.get("result"),
        "profiles": profiles,
        "members": members,
        "rm_1v1": ratings,
        "top_level_keys": list(data.keys()),
    }

def main():
    print("Read-only diagnostic. No config, roster, or generated data is modified.")
    for player, details in TARGETS.items():
        print(f"\\n===== {player} (AoE2Insights ID {details['aoe2insights_id']}) =====")
        for alias in details["aliases"]:
            try:
                status, data = request_stats("aliases", [alias])
                print(json.dumps({
                    "lookup_type": "alias",
                    "query": alias,
                    "http_status": status,
                    **summarize(data),
                }, ensure_ascii=False))
            except HTTPError as exc:
                print(json.dumps({"lookup_type": "alias", "query": alias, "http_error": exc.code}))
            except (URLError, TimeoutError, ValueError) as exc:
                print(json.dumps({"lookup_type": "alias", "query": alias, "error": str(exc)}))
            time.sleep(0.4)
        try:
            status, data = request_stats("profile_ids", [details["aoe2insights_id"]])
            print(json.dumps({
                "lookup_type": "aoe2insights_profile_id",
                "query": details["aoe2insights_id"],
                "http_status": status,
                **summarize(data),
            }, ensure_ascii=False))
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            print(json.dumps({"lookup_type": "aoe2insights_profile_id", "query": details["aoe2insights_id"], "error": str(exc)}))
        time.sleep(0.5)

if __name__ == "__main__":
    main()
