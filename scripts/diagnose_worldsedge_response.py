#!/usr/bin/env python3
"""Inspect the World's Edge GetPersonalStat response without changing roster data."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ratings import request_stats, parse_stats

PROFILE_IDS = [12359161, 3964428]  # Virus and BkB: one currently missing, one known roster account


def typed(value):
    return {"value": value, "type": type(value).__name__}


def main():
    for profile_id in PROFILE_IDS:
        print(f"\\n=== profile_id {profile_id} ===")
        data = request_stats([profile_id])
        print("top-level keys:", sorted(data.keys()))
        groups = data.get("statGroups", [])
        print("statGroups count:", len(groups))
        for index, group in enumerate(groups[:8]):
            print(f"statGroups[{index}] keys:", sorted(group.keys()))
            print("  group.id:", typed(group.get("id")))
            members = group.get("members", [])
            print("  members count:", len(members))
            for member in members[:5]:
                print("  member:", {
                    "profile_id": typed(member.get("profile_id")),
                    "alias": member.get("alias"),
                    "keys": sorted(member.keys()),
                })
        stats = data.get("leaderboardStats", [])
        print("leaderboardStats count:", len(stats))
        for stat in stats[:20]:
            print("  leaderboardStat:", {
                key: typed(stat.get(key))
                for key in ("statgroup_id", "leaderboard_id", "rating", "highestrating", "lastmatchdate")
            })
        parsed = parse_stats(data)
        print("parse_stats profile IDs:", sorted(parsed.keys()))
        print("parse_stats target:", parsed.get(profile_id))


if __name__ == "__main__":
    main()
