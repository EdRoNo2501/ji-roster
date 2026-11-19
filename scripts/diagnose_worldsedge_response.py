#!/usr/bin/env python3
"""Read-only comparison of World's Edge stats for roster accounts missing 1v1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ratings import request_stats

# Accounts flagged by the latest production run, plus BkB as a working control.
PROFILE_IDS = [
    12359161, 12989767, 12876939, 12573559, 13258119, 12950375,
    13026074, 12722759, 13190355, 12953298, 13067703, 12831320,
    13505523, 13222272, 13081631, 12820653, 13087608, 13013041,
    3964428,
]
BATCH_SIZE = 10


def main():
    for start in range(0, len(PROFILE_IDS), BATCH_SIZE):
        ids = PROFILE_IDS[start:start + BATCH_SIZE]
        print(f"\\n=== request IDs {ids} ===")
        data = request_stats(ids)
        groups_by_profile = {}
        group_ids = {}
        for group in data.get("statGroups", []):
            for member in group.get("members", []):
                pid = member.get("profile_id")
                groups_by_profile[pid] = (group, member)
                group_ids[group.get("id")] = pid

        stats_by_group = {}
        for stat in data.get("leaderboardStats", []):
            stats_by_group.setdefault(stat.get("statgroup_id"), []).append(stat)

        for pid in ids:
            pair = groups_by_profile.get(pid)
            if not pair:
                print(f"profile {pid}: NOT PRESENT in statGroups")
                continue
            group, member = pair
            stats = stats_by_group.get(group.get("id"), [])
            compact = [
                {
                    "leaderboard_id": s.get("leaderboard_id"),
                    "rating": s.get("rating"),
                    "highestrating": s.get("highestrating"),
                }
                for s in stats
            ]
            print({
                "requested_profile_id": pid,
                "returned_profile_id": member.get("profile_id"),
                "alias": member.get("alias"),
                "group_id": group.get("id"),
                "personal_statgroup_id": member.get("personal_statgroup_id"),
                "leaderboard_stats_count": len(stats),
                "leaderboard_stats": compact,
            })


if __name__ == "__main__":
    main()
