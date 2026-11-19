#!/usr/bin/env python3
"""Non-destructive diagnostic for JI roster profile IDs.

Resolves both the configured clan-tagged name and a conservative untagged
candidate through World's Edge, then checks whether configured IDs are
recognized. It never edits config/players.json or published data.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://aoe-api.worldsedgelink.com/community/leaderboard/GetPersonalStat"
HEADERS = {
    "User-Agent": "JI-Roster-Diagnostic/1.0 (+https://github.com/EdRoNo2501/ji-roster)",
    "Accept": "application/json",
}


def request(params):
    url = API + "?" + urllib.parse.urlencode({"title": "age2", **params})
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429 or 500 <= exc.code < 600:
                time.sleep(2 ** attempt)
                continue
            return {"_error": f"HTTP {exc.code}"}
        except Exception as exc:
            if attempt == 3:
                return {"_error": str(exc)}
            time.sleep(2 ** attempt)
    return {"_error": "retry limit exceeded"}


def profile_rows(payload):
    rows = payload.get("profiles") or []
    if rows:
        return rows
    found = {}
    for group in payload.get("statGroups") or []:
        for member in group.get("members") or []:
            pid = member.get("profile_id")
            if pid is not None:
                found[str(pid)] = {"profile_id": pid, "alias": member.get("alias", "")}
    return list(found.values())


def untagged(tag):
    value = tag.strip()
    if value.startswith("[JAGR]"):
        return value[len("[JAGR]"):].strip()
    for prefix in ("JAGR |", "JAGR I", "JAGR_", "JAGR "):
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    return value


def norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def main():
    config = json.loads(Path("config/players.json").read_text(encoding="utf-8"))
    players = config["players"]

    aliases = []
    for player in players:
        for candidate in dict.fromkeys((player["tag"], untagged(player["tag"]))):
            if candidate and candidate not in aliases:
                aliases.append(candidate)

    resolved = {}
    errors = []
    for offset in range(0, len(aliases), 10):
        batch = aliases[offset:offset + 10]
        payload = request({"aliases": json.dumps(batch, ensure_ascii=False, separators=(",", ":"))})
        if payload.get("_error"):
            errors.append(f"alias batch {offset // 10 + 1}: {payload['_error']}")
        for row in profile_rows(payload):
            alias = row.get("alias") or row.get("name") or ""
            pid = row.get("profile_id")
            if alias and pid is not None:
                resolved.setdefault(norm(alias), []).append((alias, int(pid)))
        time.sleep(0.8)

    known_ids = set()
    id_errors = []
    ids = list(dict.fromkeys(int(p.get("official_id", p["id"])) for p in players))
    for offset in range(0, len(ids), 10):
        batch = ids[offset:offset + 10]
        payload = request({"profile_ids": json.dumps(batch, separators=(",", ":"))})
        if payload.get("_error"):
            id_errors.append(f"ID batch {offset // 10 + 1}: {payload['_error']}")
        for row in profile_rows(payload):
            if row.get("profile_id") is not None:
                known_ids.add(int(row["profile_id"]))
        time.sleep(0.8)

    print("JI ROSTER — DIAGNÓSTICO DE IDENTIDADES (sin cambios)")
    print(f"Jugadores: {len(players)} | alias consultados: {len(aliases)}")
    print()
    print("Jugador | ID configurado | ID reconocido | Coincidencias por alias")
    print("-" * 110)
    for player in players:
        tag = player["tag"]
        configured = int(player.get("official_id", player["id"]))
        candidates = []
        for alias in dict.fromkeys((tag, untagged(tag))):
            candidates.extend(resolved.get(norm(alias), []))
        unique = sorted({pid for _, pid in candidates})
        recognized = "sí" if configured in known_ids else "no / sin respuesta"
        matches = ", ".join(f"{name} → {pid}" for name, pid in sorted(set(candidates))) or "—"
        print(f"{tag} | {configured} | {recognized} | {matches}")
    print()
    print(f"IDs reconocidos: {len(known_ids)}/{len(ids)}")
    if errors or id_errors:
        print("Errores:")
        for error in errors + id_errors:
            print(f"- {error}")
    print()
    print("NOTA: una coincidencia por alias no cambia el roster. Revisar manualmente")
    print("cualquier ID distinto, múltiples coincidencias o alias sin resultado.")


if __name__ == "__main__":
    main()
