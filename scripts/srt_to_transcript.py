"""Turn an .srt subtitle file into transcript.json (before forced alignment).

- drops sound/speaker tags like [música tensa] or [Rafael] and HTML tags
- splits "-line one / -line two" cues (two speakers) into separate lines
- joins a cue with the next when the sentence runs on (no end punctuation, short gap)
- gives words provisional timings spread over the cue; align.py fixes them

usage: python3 scripts/srt_to_transcript.py <file.srt> <media/id> "Title" [--show "Show"] [--source "..."]
"""
import argparse
import json
import os
import re
import subprocess


def ts(t):
    h, m, s = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def cues(path):
    text = open(path, encoding="utf-8-sig").read().replace("\r", "")
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n")
        m = next((re.match(r"(\S+) --> (\S+)", l) for l in lines if "-->" in l), None)
        if not m:
            continue
        body = lines[[i for i, l in enumerate(lines) if "-->" in l][0] + 1:]
        yield ts(m.group(1)), ts(m.group(2)), body


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\[[^\]]*\]", "", s)
    s = re.sub(r"\([^)]*\)", "", s)
    s = s.replace("♪", "")
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("srt")
    ap.add_argument("dir")
    ap.add_argument("title")
    ap.add_argument("--show", default="")
    ap.add_argument("--source", default="")
    a = ap.parse_args()

    raw = []  # (start, end, text)
    for s, e, body in cues(a.srt):
        # a leading dash marks a new speaker within the cue
        parts, cur = [], []
        for line in body:
            if re.match(r"^\s*[-–]", line) and cur:
                parts.append(" ".join(cur))
                cur = []
            cur.append(re.sub(r"^\s*[-–]\s*", "", line))
        parts.append(" ".join(cur))
        parts = [clean(p) for p in parts]
        parts = [p for p in parts if re.search(r"\w", p)]
        if not parts:
            continue
        total = sum(len(p) for p in parts)
        t = s
        for p in parts:
            d = (e - s) * len(p) / total
            raw.append([t, t + d, p, len(parts) > 1])
            t += d

    # join run-on sentences across cues (same speaker, no end punctuation)
    segs = []
    for s, e, txt, multi in raw:
        if segs:
            prev = segs[-1]
            if (not re.search(r"[.?!…:]$", prev[2]) and not multi and not prev[3]
                    and s - prev[1] < 0.6 and len((prev[2] + " " + txt).split()) <= 26):
                prev[1], prev[2] = e, prev[2] + " " + txt
                continue
        segs.append([s, e, txt, multi])

    out = []
    for s, e, txt, _ in segs:
        ws = txt.split()
        total = sum(len(w) for w in ws)
        t, words = s, []
        for w in ws:
            d = (e - s) * len(w) / total
            words.append({"w": w, "s": round(t, 2), "e": round(t + d, 2)})
            t += d
        out.append({"start": round(s, 2), "end": round(e, 2), "text": txt, "words": words})

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
         os.path.join(a.dir, "audio.mp3")], capture_output=True, text=True).stdout.strip())
    T = {"title": a.title, "show": a.show, "source": a.source, "duration": round(dur),
         "transcriptSource": "subtitles", "segments": out}
    json.dump(T, open(os.path.join(a.dir, "transcript.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(out)} lines, {sum(len(x['words']) for x in out)} words")


main()
