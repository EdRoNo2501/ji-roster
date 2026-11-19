# Jaguares Imperiales — AoE2 Clan Roster

A live clan roster and country leaderboards for **Jaguares Imperiales (JI)**. Ratings are fetched from the Age of Empires II ranked-stats API (World's Edge) and displayed by a static site on GitHub Pages.

## Project structure

```text
config/players.json                 JI members (profile IDs, display tags, countries)
config/{mexico,colombia,peru}.json  Country leaderboard configuration
scripts/fetch_ratings.py           Fetches ratings and writes docs/data/*.json
scripts/links.py                    Builds linked-account data
docs/index.html                     Static roster and leaderboard page
docs/assets/logo_JI.jpg              Official Jaguares Imperiales clan logo
.github/workflows/update-roster.yml    GitHub Actions updater
```

## Before publishing

1. Add the clan's real members to `config/players.json`. The starter file intentionally has an empty roster; no player IDs or members have been fabricated.
2. Review the country ranking lists in `config/mexico.json`, `config/colombia.json`, and `config/peru.json`. These are retained from the source project and are independent country leaderboards—not JI member lists.
3. The official Jaguares Imperiales logo is installed in `docs/assets/logo_JI.jpg` and used by the page.
4. Set up a new GitHub repository (suggested name: `ji-roster`) and push this project.

## First run

Run from the repository root: `python scripts/fetch_ratings.py`. This uses Python's standard library. It fetches configured players and updates `docs/data/`.

The country leaderboards are kept configurable in JSON. To populate or refresh their data, check the corresponding configs and run the fetch script.

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
- Emblem: `docs/assets/logo_JI.svg`
