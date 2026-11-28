#!/usr/bin/env python3
"""Turn Rumbo's clip scripts into the clip bank the game plays.

  courses/rumbo/clips.json  ->  media/rumbo/<kind>/<id>.mp3 + media/rumbo/bank.json

1. Voices: Fish Audio speaks each clip with its speaker's voice (public/rumbo/data.js SPEAKERS) at its
   tier's speed. Fish's output is cached in courses/rumbo/audio/ by hash of model, voice, speed and text.
2. Whisper (large-v3, Spanish) listens to every clip; what it heard goes into the bank, and
   scripts/rumbo/check_bank.mjs compares it with the facts.
3. Alignment: the clips are joined into one track and scripts/align.py (the episodes' forced aligner)
   times every word, so clips get the same features as episode lines (speech rate and so on).

  .venv/bin/python scripts/rumbo/build_bank.py            # everything missing
  .venv/bin/python scripts/rumbo/build_bank.py --only r-  # only clips whose id starts with r-

  .venv/bin/python scripts/rumbo/build_bank.py --say      # stand-in voices from macOS `say` (no Fish
                                                           # account needed; for development only)

The Fish Audio key (FISH_API_KEY) comes from .env in the project, as in build_course.py.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_course  # noqa: E402  (fish(), load_env())

SRC = ROOT / "courses" / "rumbo" / "clips.json"
CACHE = ROOT / "courses" / "rumbo" / "audio"
OUT = ROOT / "media" / "rumbo"
MODEL = build_course.MODEL
BITRATE = "48k"
GAP = 1.0


def data_js():
    js = "import('./public/rumbo/data.js').then(m => console.log(JSON.stringify({S: m.SPEAKERS, T: m.TIER_SPEED})))"
    r = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def cache_path(voice, speed, text):
    h = hashlib.sha1(f"{MODEL}|{voice}|{speed}|{text}".encode()).hexdigest()[:12]
    return CACHE / f"{h}.mp3"


def fish(text, voice, speed, out):
    """build_course.fish() with the speed as an argument (it reads a module global, unsafe in threads)."""
    import time
    import urllib.request
    body = json.dumps({"text": text, "reference_id": voice, "format": "mp3", "mp3_bitrate": 128, "normalize": True,
                       "temperature": 0.7, "top_p": 0.7, "prosody": {"speed": speed}}).encode()
    err = ""
    for attempt in range(6):
        req = urllib.request.Request(build_course.FISH_URL, data=body, method="POST", headers={
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


SAY_VOICES = ["Paulina", "Eddy (Spanish (Mexico))", "Flo (Spanish (Mexico))", "Reed (Spanish (Mexico))", "Sandy (Spanish (Mexico))",
              "Rocko (Spanish (Mexico))", "Shelley (Spanish (Mexico))", "Grandpa (Spanish (Mexico))", "Grandma (Spanish (Mexico))"]


def say(text, voice, speed, out):
    """Stand-in speech from macOS (voice is "say:<name>")."""
    with tempfile.TemporaryDirectory() as td:
        aiff = Path(td) / "a.aiff"
        subprocess.run(["say", "-v", voice[4:], "-r", str(int(175 * speed)), "-o", str(aiff), text], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(aiff), "-b:a", "128k", str(out)], check=True)


def whisper(mp3):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
        r = subprocess.run(["whisper-cli", "-m", str(ROOT / "models" / "ggml-large-v3.bin"), "-l", "es", "-nt", "-np", "-f", str(wav)],
                           capture_output=True, text=True)
    return " ".join(r.stdout.split())


def align(clips):
    """Word times for every clip, from one joined track through scripts/align.py."""
    import numpy as np
    import soundfile as sf
    import align as aligner
    sr = 16000
    with tempfile.TemporaryDirectory() as td:
        audio, segs, t = [np.zeros(int(GAP * sr), dtype="float32")], [], GAP
        for c in clips:
            wav = Path(td) / "c.wav"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(OUT / c["file"]), "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", str(wav)], check=True)
            a, _ = sf.read(wav, dtype="float32")
            d = len(a) / sr
            words = c["text"].split()
            total = sum(len(w) + 1 for w in words)
            at, ws = t, []
            for w in words:
                dw = (len(w) + 1) / total * d
                ws.append({"w": w, "s": round(at, 2), "e": round(at + dw, 2)})
                at += dw
            segs.append({"start": round(t, 2), "end": round(t + d, 2), "text": c["text"], "words": ws, "id": c["id"]})
            audio += [a, np.zeros(int(GAP * sr), dtype="float32")]
            c["dur"] = round(d, 2)
            c["_t"] = t
            t += d + GAP
        sf.write(Path(td) / "audio16k.wav", np.concatenate(audio), sr, subtype="PCM_16")
        (Path(td) / "transcript.json").write_text(json.dumps({"segments": segs}, ensure_ascii=False))
        aligner.split_long = lambda s, max_words=30: [s]  # one clip, one line
        aligner.main(td)
        out = json.loads((Path(td) / "transcript.json").read_text())
    by = {s["id"]: s for s in out["segments"]}
    for c in clips:
        t0 = c.pop("_t")
        c["words"] = [{"w": w["w"], "s": round(max(0, w["s"] - t0), 2), "e": round(max(0, w["e"] - t0), 2)} for w in by[c["id"]]["words"]]


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    use_say = "--say" in sys.argv
    D = data_js()
    src = json.loads(SRC.read_text())["clips"]
    bank_file = OUT / "bank.json"
    old = {c["id"]: c for c in json.loads(bank_file.read_text())["clips"]} if bank_file.exists() else {}
    CACHE.mkdir(parents=True, exist_ok=True)

    jobs = []
    for c in src:
        sp = D["S"][c["speaker"]]
        c["voice"], c["speed"] = sp["voice"], D["T"][str(c["tier"])]
        if use_say:
            c["voice"] = "say:" + SAY_VOICES[list(D["S"]).index(c["speaker"]) % len(SAY_VOICES)]
        c["file"] = f'{c["kind"]}/{c["id"]}.mp3'
        if not cache_path(c["voice"], c["speed"], c["text"]).exists():
            jobs.append(c)
    if jobs:
        if not use_say:
            build_course.load_env()
        print(f"{'say' if use_say else 'Fish'}: {len(jobs)} clips to speak")
        with cf.ThreadPoolExecutor(build_course.CONCURRENCY) as ex:
            list(ex.map(lambda c: (say if use_say else fish)(c["text"], c["voice"], c["speed"], cache_path(c["voice"], c["speed"], c["text"])), jobs))

    # a clip is (re)built when it's new or its text, voice or speed changed
    todo = []
    for c in src:
        o = old.get(c["id"])
        same = o and o.get("text") == c["text"] and o.get("voice") == c["voice"] and o.get("speed") == c["speed"] and (OUT / c["file"]).exists()
        if same:
            c.update({k: o[k] for k in ("dur", "words", "heard") if k in o})
        elif c["id"].startswith(only):
            todo.append(c)
    print(f"{len(todo)} clips to encode, hear and align")
    for c in todo:
        (OUT / c["file"]).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(cache_path(c["voice"], c["speed"], c["text"])), "-ac", "1", "-ar", "44100",
                        "-b:a", BITRATE, "-codec:a", "libmp3lame", str(OUT / c["file"])], check=True)
    with cf.ThreadPoolExecutor(2) as ex:
        for c, heard in zip(todo, ex.map(lambda c: whisper(OUT / c["file"]), todo)):
            c["heard"] = heard
            print(f"  {c['id']}: {heard[:90]}")
    if todo:
        align(todo)

    keep = [c for c in src if "words" in c]
    for c in keep:
        c.pop("device", None)
    bank = {"model": MODEL, "clips": [{k: c[k] for k in ("id", "kind", "speaker", "tier", "facts", "text", "file", "dur", "words", "heard", "voice", "speed") if k in c}
                                      for c in keep]}
    # files of clips no longer in the source
    names = {c["file"] for c in keep}
    for p in OUT.glob("*/*.mp3"):
        if f"{p.parent.name}/{p.name}" not in names:
            p.unlink()
    bank_file.write_text(json.dumps(bank, ensure_ascii=False))
    print(f"{bank_file}: {len(keep)} clips")


if __name__ == "__main__":
    main()
