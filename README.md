# Jaguares Imperiales — AoE2 Clan Roster

A live clan roster and country leaderboards for **Jaguares Imperiales (JI)**. Ratings are fetched from the Age of Empires II ranked-stats API (World's Edge) and displayed by a static site on GitHub Pages.

## Project structure

```text
config/players.json                 JI members (profile IDs, display tags, countries)
config/*.json                      Clan and national rosters by country
scripts/fetch_ratings.py           Fetches ratings and writes docs/data/*.json
scripts/links.py                    Builds linked-account data
docs/index.html                     Static roster and leaderboard page
docs/assets/logo_JI.jpg              Official Jaguares Imperiales clan logo
.github/workflows/update-roster.yml    GitHub Actions updater
```

## Before publishing

1. The 30 members supplied for Jaguares Imperiales are registered in `config/players.json`, with their country and explicit `member_status` (`active` or `inactive`).
2. The clan roster shows active members first and inactive members in a separate section. Gameplay inactivity (based on recent ranked games) is tracked independently and does not alter clan membership status.
3. The national rosters include every JI member from Colombia, México, Argentina, Perú, Venezuela, Uruguay, Chile, and Costa Rica. Active members are listed first and ranked; inactive clan members remain visible in a separate section without a competitive rank.
4. The official Jaguares Imperiales logo is installed in `docs/assets/logo_JI.jpg` and used by the page.

## First run

Run from the repository root: `python scripts/fetch_ratings.py`. This uses Python's standard library. It fetches configured players and updates `docs/data/`.

The national rosters are kept configurable in JSON. Each one contains all JI members from that country, with active and inactive membership status; the fetch script updates them alongside the clan roster.

## GitHub Pages

In the repository: **Settings → Pages → Deploy from a branch → `main` → `/docs`**. Once published, the page URL will be `https://YOUR-USERNAME.github.io/ji-roster/`.

## Automation

The workflow in `.github/workflows/update-roster.yml` can run on its built-in schedule and manually through the Actions tab. Review its schedule and GitHub permissions before enabling it. It commits updated data only when files changed.

The original project used an external `cron-job.org` trigger because GitHub schedule timing may be delayed. External scheduling is optional; set it up only after the workflow works manually. **Do not paste a personal access token into the repository or HTML.** Store tokens only in the scheduler's secret/header configuration if an external trigger is used.

## Player IDs

The `id` values in the config are aoe2insights profile IDs. Some accounts may need an `official_id` if their API ID differs. Use `tag` to override the display name, and `country` for the roster flag.

## Data-source caveat

The stats API is unofficially documented and may change. The code preserves prior data when a lookup fails rather than replacing it with blanks. Verify that data is current after the first manual run.

## Customization

- Clan name and tag: `config/players.json` (`clan_name`, `clan_tag`)
- Clan roster: `config/players.json` → `players`
- Country rankings: respective files in `config/`
- Design: `docs/index.html` (colors, fonts, layout)
- Emblem: `docs/assets/logo_JI.jpg`
