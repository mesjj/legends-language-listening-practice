#!/usr/bin/env python3
"""Build a course (sentences written for a learner) into an episode the game can play.

  courses/<id>/course.json  ->  media/<id>/audio.mp3 + transcript.json

Each sentence is spoken by Fish Audio (one clip per sentence, cached in courses/<id>/audio/ by
hash of model, voice, speed and text), the clips are joined with a pause between them, and the
transcript carries, per line, the lesson: the verb (where it is in the sentence, its forms and
meaning), the Spanish translation, the hint for the gap, and the meaning of the other words.
The course's zones (levels) go in the transcript too; the game uses them instead of its own.

  python3 scripts/build_course.py courses/verbos-irregulares          # build (makes missing clips)
  python3 scripts/build_course.py courses/verbos-irregulares --check  # Whisper listens to every clip

The Fish Audio key (FISH_API_KEY) comes from .env in the project, or the file FISH_ENV names.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = Path(os.environ.get("FISH_ENV", ROOT / ".env"))  # FISH_API_KEY=…
FISH_URL = "https://api.fish.audio/v1/tts"
MODEL = "s2.1-pro"
SPEED = 0.85          # a little slow: she's a beginner, and Despacio slows it further
GAP = 0.8             # seconds of silence between sentences
CONCURRENCY = 4       # the account allows 5


def load_env():
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def tokens(s):
    return s.split()


def bare(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def find_verb(words, f):
    """Indices of the verb's words in the sentence, in order ("have seen" in "I have never seen ...")."""
    want, at, i = [bare(x) for x in f.split()], [], 0
    for k, w in enumerate(words):
        if i < len(want) and bare(w) == want[i]:
            at.append(k)
            i += 1
    if i < len(want):
        raise SystemExit(f'verb "{f}" not found in "{" ".join(words)}"')
    return at


def fish(text, voice, out):
    body = json.dumps({"text": text, "reference_id": voice, "format": "mp3", "mp3_bitrate": 128,
                       "normalize": True, "temperature": 0.7, "top_p": 0.7, "prosody": {"speed": SPEED}}).encode()
    err = ""
    for attempt in range(6):
        req = urllib.request.Request(FISH_URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {os.environ['FISH_API_KEY']}", "model": MODEL, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) > 1000:
                out.write_bytes(data)
                return
            err = f"short response ({len(data)} bytes)"
        except Exception as ex:  # rate limits and timeouts: wait and retry
            err = str(ex)
        time.sleep(2 + attempt * 3)
    raise SystemExit(f"Fish failed for {text!r}: {err}")


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


MODES = ["verb", "vocab", "gap"]          # each verb has three sentences: for the verb, for word by word and the whole sentence, and for write the verb
TEMPLATES = ["paramo", "cienaga", "selva", "llano", "ruinas"]  # the game's zones lend monsters and bosses


def lines_of(course):
    """Every sentence, zone by zone: the zone's level-1 sentences, then level 2, then level 3."""
    verbs = {v["v"]: {**v, "group": g["name"]} for g in course["groups"] for v in g["verbs"]}
    out = []
    for zi, z in enumerate(course["zones"]):
        for lvl, mode in enumerate(MODES):
            for name in z["verbs"]:
                V = verbs[name]
                out.append({**V, **V["x"][lvl], "mode": mode, "zone": zi})
    return out


def split(xs, size=6):
    """Fights of at most `size` lines, as even as possible."""
    k = -(-len(xs) // size)
    return [xs[i * len(xs) // k:(i + 1) * len(xs) // k] for i in range(k)]


def word_items(L, si):
    """The cards of level 2: each word or phrase of the sentence's glosses, where it is in the sentence."""
    ws = [bare(w) for w in L[si]["s"].split()]
    out = []
    for k, (en, _) in enumerate(L[si]["g"]):
        want = [bare(x) for x in en.split()]
        a = next((i for i in range(len(ws)) if ws[i:i + len(want)] == want), None)
        if a is None:
            raise SystemExit(f'gloss "{en}" not found in "{L[si]["s"]}"')
        out.append({"si": si, "a": a, "b": a + len(want), "k": k})
    return out


def word_fights(L, lines, size=8):
    """Level 2 fights: a few sentences each, their words taken in turns so the same sentence isn't asked twice running."""
    groups, cur = [], []
    for si in lines:
        cur.append(si)
        if sum(len(L[x]["g"]) for x in cur) >= size - 1:
            groups.append(cur); cur = []
    if cur:
        if groups and sum(len(L[x]["g"]) for x in cur) < 3: groups[-1] += cur
        else: groups.append(cur)
    fights = []
    for g in groups:
        per = [word_items(L, si) for si in g]
        items = [it for k in range(max(map(len, per))) for p in per if k < len(p) for it in [p[k]]]
        fights.append({"mode": "word", "lines": g, "items": items})
    return fights


def zones_of(course, L):
    """Per zone, four ways to study it, each its own run of fights whose last is the boss: the verb,
    word by word, write the verb, and the whole sentence. The player picks any of them on the map."""
    out = []
    for zi, z in enumerate(course["zones"]):
        mine = [i for i, l in enumerate(L) if l["zone"] == zi]
        by = {m: [i for i in mine if L[i]["mode"] == m] for m in MODES}
        fights = [{"mode": "verb", "lines": f} for f in split(by["verb"])] + word_fights(L, by["vocab"])
        fights.append({"mode": "gap", "lines": by["gap"]})
        fights += [{"mode": "vocab", "lines": f} for f in split(by["vocab"])]
        out.append({"id": z["id"], "name": z["name"], "template": TEMPLATES[zi % len(TEMPLATES)], "lvl": [1 + 3 * zi, 3 + 3 * zi],
                    "blurb": ", ".join(z["verbs"]), "fights": fights})
    return out


def clip_path(cdir, course, line):
    h = hashlib.sha1(f"{MODEL}|{course['voice']}|{SPEED}|{line['s']}".encode()).hexdigest()[:12]
    return cdir / "audio" / f"{h}.mp3"


def build(cdir):
    course = json.loads((cdir / "course.json").read_text())
    L = lines_of(course)
    for line in L:
        line["at"] = find_verb(tokens(line["s"]), line["f"])
    (cdir / "audio").mkdir(exist_ok=True)
    todo = [l for l in L if not clip_path(cdir, course, l).exists()]
    if todo:
        load_env()
        print(f"Fish: {len(todo)} clips to make")
        with cf.ThreadPoolExecutor(CONCURRENCY) as ex:
            list(ex.map(lambda l: fish(l["s"], course["voice"], clip_path(cdir, course, l)), todo))

    # one wav per clip and a silence, joined, then one mp3; times from the wavs' exact lengths
    out = ROOT / "media" / course["id"]
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_build"
    tmp.mkdir(exist_ok=True)
    rate = 44100
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={rate}:cl=mono", "-t", str(GAP),
                    "-c:a", "pcm_s16le", str(tmp / "gap.wav")], check=True)
    segs, parts, t = [], [], GAP
    parts.append(tmp / "gap.wav")
    for i, line in enumerate(L):
        wav = tmp / f"{i:03d}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(clip_path(cdir, course, line)), "-ac", "1", "-ar", str(rate),
                        "-c:a", "pcm_s16le", str(wav)], check=True)
        d = (wav.stat().st_size - 44) / (2 * rate)
        words = tokens(line["s"])
        # word times spread by length (the game plays whole sentences; these only feed hints and gaps)
        total = sum(len(w) + 1 for w in words)
        at, ws = t + 0.05, []
        for w in words:
            dw = (len(w) + 1) / total * (d - 0.1)
            ws.append({"w": w, "s": round(at, 2), "e": round(at + dw, 2)})
            at += dw
        segs.append({
            "start": round(t, 2), "end": round(t + d, 2), "text": line["s"], "words": ws,
            "lesson": {"mode": line["mode"], "v": line["v"], "past": line["past"], "pp": line["pp"], "es": line["es"], "at": line["at"],
                       "hint": line["h"], "t": line["t"], "gloss": line["g"], "group": line["group"]},
        })
        parts += [wav, tmp / "gap.wav"]
        t += d + GAP
    (tmp / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-ac", "1", "-b:a", "96k", "-codec:a", "libmp3lame", str(out / "audio.mp3")], check=True)
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    n = len(segs)
    T = {"title": course["title"], "show": course["show"], "source": "course", "lang": "en", "duration": round(t, 2),
         "segments": segs, "zones": zones_of(course, L), "levels": course["levels"]}
    (out / "transcript.json").write_text(json.dumps(T, ensure_ascii=False))
    print(f"{out}: {n} sentences, {t / 60:.1f} min of audio")


def check(cdir):
    """Whisper (large-v3, English) listens to every clip; prints the ones that don't say the sentence."""
    course = json.loads((cdir / "course.json").read_text())
    bad = 0
    for line in lines_of(course):
        mp3 = clip_path(cdir, course, line)
        wav = mp3.with_suffix(".16k.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
        r = subprocess.run(["whisper-cli", "-m", str(ROOT / "models" / "ggml-large-v3.bin"), "-l", "en", "-nt", "-np", "-f", str(wav)],
                           capture_output=True, text=True)
        wav.unlink()
        heard = " ".join(r.stdout.split())
        same = [bare(w) for w in line["s"].split()] == [bare(w) for w in heard.split()]
        if not same:
            bad += 1
            print(f"  ✗ {line['s']}\n    heard: {heard}")
    print(f"{bad} of {len(lines_of(course))} clips differ from their text")


if __name__ == "__main__":
    d = Path(sys.argv[1]).resolve()
    check(d) if "--check" in sys.argv else build(d)
