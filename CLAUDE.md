# Notes for Claude

Read this first, then `README.md`. The README describes every feature in detail and is kept up to date with each change.

## What this is

Oído is a local Spanish listening trainer. It has two parts:

- **Listening pages:** `index.html`, `play.html` and `episodes.html`, written in English.
- **Leyendas:** `rpg.html`, an action RPG where every attack is a listening exercise on the next line of an episode. Its interface is in Spanish, and all its content is original, drawn from Colombian legends.

The owner is an advanced learner training listening at native speed, so **transcripts must be close to 100% accurate**. Never "fix" a line by guessing; when in doubt, flag it.

## Run it

```sh
npm install
npm start          # http://127.0.0.1:8790/  (the game: /rpg.html)
```

- Node 18+. There is no build step: the browser loads plain ES modules from `public/`.
- `server.js` serves `public/` and `media/`, and runs the APIs: episodes, transcript edits and flags, the Anki bridge, and Claude "explain".
- Data goes to `data/`, which is created on first start.
- Settings come from environment variables: `PORT`, `HOST`, `MEDIA_DIR`, `DATA_DIR`, `ANKI_URL`/`ANKI_DECK`, `CLAUDE_MODEL`/`CLAUDE_BIN`, `ONLINE=1` (login, per-player saves, only the game), `BASE_PATH` and `LEARN_LANG`.
- "Explain" and La encrucijada's feedback shell out to the `claude` CLI, or use `ANTHROPIC_API_KEY` if it is set. Use the CLI. Never lift its subscription OAuth token into other code.
- Anki features need Anki running with AnkiConnect. Without it they show a message and the rest works.

## Episodes

The repo ships one episode: `media/verbos-irregulares`, a short course built by `scripts/build_course.py` from `courses/verbos-irregulares/course.json`, with Fish Audio TTS.

TV, film and talk-show episodes are **not** in the repo: they're copyrighted, so never commit them (see `.gitignore`). An episode is just `media/<id>/audio.mp3` plus `media/<id>/transcript.json`, a set of segments `{start, end, text, words:[{w,s,e}]}`. To add your own:

- `scripts/add-episode.sh <youtube-url>` runs Whisper, a Claude correction pass and forced alignment. It needs yt-dlp, ffmpeg and whisper-cpp, plus `models/ggml-large-v3.bin` and `models/ggml-silero-v5.1.2.bin`; download those two from the whisper.cpp releases.
- `scripts/add-subtitled.sh` and `scripts/add-dubbed.sh` start from subtitle files.
- Each episode's `transcript.json` has `names`: the non-Spanish proper names, which scoring doesn't count when wrong. The import scripts make it with `scripts/find_names.mjs`; run that by hand for an episode added another way.

## The game's code (`public/rpg/`)

| File | What's in it |
|---|---|
| `main.js` | All screens and game flow: village, map, fights, loot, bosses' rules, dice, tooltips, options |
| `engine.js` | Rules: stats, items, affixes, encounters, streak dice (`streakRoll`), crafting |
| `data.js` | Content: classes, zones, monsters, bosses, item bases (`BASE`, high-level `BANDS`), sets, runes, gems |
| `figure.js`, `look.js` | The paper-doll figure, from the LPC sprite atlas in `rpg/lpc/` |
| `boss.js`, `fx.js`, `sfx.js`, `music.js` | Boss art and intros, hit effects, synthesized sound, music |
| `../listen-core.js` | Shared with the listening pages: scoring, `playable()` lines, blanks for the gap exercise |

Key ideas:
- **Zones are fixed stretches of the episode.** Its lines are shared among the normal groups. The boss only appears once half of them are mastered, and brings the unheard and most-missed ones.
- **Each zone has three bosses** (`ZONES` `bosses`). An episode meets one, picked at random and kept in `ch.bossPick` until the episode is restarted; always go through `zoneBoss(z)` in `main.js`, never `z.boss`.
- **Each slot of the road draws one of five zones** (`ZONE_VARIANTS` in `data.js`), kept per episode in `ch.zonePick` until it's restarted. `applyZonePicks()` in `main.js` copies the drawn zone's name, monsters, bosses, scene and music onto the slot's object; progress stays keyed by slot id. The hells' Abismos name their descents (`descentName`).
- **The Abismo's descents** carry on to the episode's end.
- **El Remolino** is the last level. It opens when the whole episode is mastered and is rebuilt from the lines you struggled with most.
- **Progress is per episode** (`ch.zonesByEp`), and a new episode's zone levels are shifted to the character's level.
- The character is saved in `localStorage` (`rpg`), or on the server when `ONLINE=1`.
- In the browser console, `window.leyendas` exposes `S`, `ch`, `E` and render functions for debugging.

## Art

The generated art is committed, so you only need these when changing art:

- **Item, figure and icon art:** `node scripts/lpc_items.mjs && .venv/bin/python scripts/build_lpc.py` takes about 2.5 minutes. It needs the LPC source in `.lpc-cache/`, which `lpc_items.mjs` downloads, and a Python venv with Pillow.
- **Set ornaments:** `scripts/custom_art.py`.
- **The bodhisattva and Guru Rinpoche sets:** `scripts/orig_art.py` draws their pieces from scratch in every frame. LPC layers are only measured for where the body is. `build_lpc.py` calls it.
- **Scenes:** `scripts/build_scenes.py`.
- **Bosses:** `scripts/build_bosses.py`.
- **Credits:** `public/rpg/**/CREDITS*.txt`. LPC art is CC-BY-SA / GPL / OGA-BY, so keep the credits with it.

## Conventions

- Game content stays original. Don't recreate characters, names or art from existing games.
- **Game text is Spanish, the listening pages English.** Write game strings in the same plain voice as the existing ones. An English interface is a translation layer (`public/rpg/i18n.js`, see the README). After changing game text, run `node scripts/i18n/extract.mjs && node scripts/i18n/translate.mjs`. Prefer whole sentences in templates over words glued from conditionals (`dominad${x ? "os" : "as"}`), which can't be matched; when you can't, add an entry to `public/rpg/i18n/en.manual.json`. Wrap anything the player is learning (Spanish lines, typed answers) in an element the translator skips (`translate="no"`).
- **Relative URLs only.** The app may be served under a subpath such as `/leyendas/`.
- **Check every UI change at phone width (390px)** as well as desktop.
- **Update `README.md`** with every feature change. It's the spec.
- **Testing:** Playwright with the `chrome` channel works well. In tests:
  - Route `**/api/review/answer` (the Anki bridge) so tests never write to a real Anki.
  - Set `S.F.plays = 1` before submitting an answer. The game refuses answers until the line has been heard ("Escucha primero").
  - Calling `renderMap()` directly throws a harmless `onclick` error from the Anki section when Anki is not running.
- Python scripts run with `.venv/bin/python`.
