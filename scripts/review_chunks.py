"""Prepare and apply a two-source correction pass on transcript.json.

prepare: lines up YouTube auto-caption words (json3) with each transcript line by
time and writes review chunks for a corrector (Claude), one line per segment:
    #12 [1:02.4-1:06.0] W: whisper text | Y: youtube words
    +G3 [1:06.9-1:08.2] W: (nothing) | Y: words only youtube heard
With English subtitles (subtitles.en.json3, e.g. a dubbed film) each line also gets
    | E: the English subtitle words at that time

apply: reads the corrector's JSON outputs ({"12": "new text", "G3": null}) and
updates transcript.json. Unchanged words keep their timings; changed words get
interpolated timings; {braced} words are flagged uncertain ("u": 1).

usage:
  python3 -I scripts/review_chunks.py prepare media/<id> --chunks 6
  python3 -I scripts/review_chunks.py apply media/<id> corrections1.json [...]
"""
import difflib
import json
import os
import re
import sys
import unicodedata


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]", "", w)


def ts(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def yt_words(path):
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for ev in d.get("events", []):
        if "segs" not in ev:
            continue
        t0 = ev.get("tStartMs", 0)
        for s in ev["segs"]:
            t = (t0 + s.get("tOffsetMs", 0)) / 1000
            for piece in s.get("utf8", "").split():
                if piece.startswith("[") and piece.endswith("]"):
                    continue
                out.append({"w": piece, "s": t})
    out.sort(key=lambda x: x["s"])
    for i, w in enumerate(out):
        nxt = out[i + 1]["s"] if i + 1 < len(out) else w["s"] + 0.5
        w["e"] = min(nxt, w["s"] + 0.8)
    return out


def build_items(d):
    # Always work from the pre-review transcript so ids match the chunks.
    src = os.path.join(d, "transcript.whisper.json")
    if not os.path.exists(src):
        src = os.path.join(d, "transcript.json")
    T = json.load(open(src, encoding="utf-8"))
    # reference words: aligned official subtitles if present, else YouTube auto-captions
    ref = os.path.join(d, "subtitles.json3")
    Y = yt_words(ref if os.path.exists(ref) else os.path.join(d, "audio.es-orig.json3"))
    segs = T["segments"]
    starts = [s["start"] for s in segs]
    per_seg = [[] for _ in segs]
    gaps = []  # lists of yt words outside any segment
    import bisect

    for w in Y:
        i = bisect.bisect_right(starts, w["s"] + 0.25) - 1
        if i >= 0 and w["s"] <= segs[i]["end"] + 0.25:
            per_seg[i].append(w)
        elif i + 1 < len(segs) and w["s"] >= segs[i + 1]["start"] - 0.25:
            per_seg[i + 1].append(w)
        else:
            if gaps and gaps[-1]["after"] == i and w["s"] - gaps[-1]["words"][-1]["e"] < 1.5:
                gaps[-1]["words"].append(w)
            else:
                gaps.append({"after": i, "words": [w]})
    # English subtitles, if any: only a guide to meaning, so just the words around each line
    en_path = os.path.join(d, "subtitles.en.json3")
    EN = yt_words(en_path) if os.path.exists(en_path) else None
    T["_en"] = EN
    items = []
    gi = 0
    for i, s in enumerate(segs):
        while gi < len(gaps) and gaps[gi]["after"] < i:
            items.append(("G", gi, gaps[gi]))
            gi += 1
        items.append(("S", i, s, per_seg[i]))
    while gi < len(gaps):
        items.append(("G", gi, gaps[gi]))
        gi += 1
    return T, items, gaps


def en_between(EN, a, b):
    if EN is None:
        return ""
    return " | E: " + " ".join(w["w"] for w in EN if a - 0.3 <= w["s"] <= b + 0.3)


def prepare(d, nchunks):
    T, items, _ = build_items(d)
    EN = T.pop("_en", None)
    lines = []
    for it in items:
        if it[0] == "S":
            _, i, s, yw = it
            if s.get("edited"):
                continue  # corrected by hand already
            y = " ".join(w["w"] for w in yw)
            lines.append(f"#{i} [{ts(s['start'])}-{ts(s['end'])}] W: {s['text']} | Y: {y}{en_between(EN, s['start'], s['end'])}")
        else:
            _, gi, g = it
            ws = g["words"]
            lines.append(f"+G{gi} [{ts(ws[0]['s'])}-{ts(ws[-1]['e'])}] W: (nothing) | Y: {' '.join(w['w'] for w in ws)}{en_between(EN, ws[0]['s'], ws[-1]['e'])}")
    out = os.path.join(d, "review")
    os.makedirs(out, exist_ok=True)
    size = -(-len(lines) // nchunks)
    for k in range(nchunks):
        chunk = lines[k * size:(k + 1) * size]
        # a little context from the neighbours, marked as such
        before = lines[max(0, k * size - 4):k * size]
        after = lines[(k + 1) * size:(k + 1) * size + 4]
        with open(os.path.join(out, f"chunk{k + 1}.txt"), "w", encoding="utf-8") as f:
            if before:
                f.write("CONTEXT BEFORE (do not correct):\n" + "\n".join(before) + "\n\n")
            f.write("LINES TO CORRECT:\n" + "\n".join(chunk) + "\n")
            if after:
                f.write("\nCONTEXT AFTER (do not correct):\n" + "\n".join(after) + "\n")
    print(f"{len(lines)} lines -> {nchunks} chunks in {out}/")


def retime(old_words, new_text, span_start, span_end):
    """Map new tokens onto old timed words; interpolate the rest."""
    toks = new_text.split()
    flags = [bool(re.match(r"^\{.*\}[^\w]*$|^[¿¡]?\{", t)) for t in toks]
    toks = [t.replace("{", "").replace("}", "") for t in toks]
    A = [norm(w["w"]) for w in old_words]
    B = [norm(t) for t in toks]
    res = [None] * len(toks)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(j2 - j1):
                o = old_words[i1 + k]
                res[j1 + k] = {"w": toks[j1 + k], "s": o["s"], "e": o["e"]}
    # interpolate unmatched runs between known neighbours
    j = 0
    while j < len(toks):
        if res[j] is not None:
            j += 1
            continue
        k = j
        while k < len(toks) and res[k] is None:
            k += 1
        lo = res[j - 1]["e"] if j > 0 else span_start
        hi = res[k]["s"] if k < len(toks) else span_end
        if hi < lo:
            hi = lo
        total = sum(len(toks[x]) + 1 for x in range(j, k))
        at = lo
        for x in range(j, k):
            dur = (hi - lo) * (len(toks[x]) + 1) / total
            res[x] = {"w": toks[x], "s": round(at, 2), "e": round(at + dur, 2), "c": 1}
            at += dur
        j = k
    for x, f in enumerate(flags):
        if f:
            res[x]["u"] = 1
    return res


def apply(d, files):
    T, items, gaps = build_items(d)
    T.pop("_en", None)
    fixes = {}
    for f in files:
        fixes.update(json.load(open(f, encoding="utf-8")))
    segs = T["segments"]
    changed = added = dropped = 0
    # reviewed segments: crosscheck flags are now stale
    for s in segs:
        if not s.get("edited"):
            for w in s["words"]:
                w.pop("u", None)
    for key, text in fixes.items():
        if key.startswith("G"):
            continue
        i = int(key)
        if i >= len(segs) or segs[i].get("edited"):
            continue
        if not text:
            segs[i]["drop"] = True  # hallucinated line
            dropped += 1
            continue
        s = segs[i]
        s["words"] = retime(s["words"], text.strip(), s["start"], s["end"])
        s["text"] = " ".join(w["w"] for w in s["words"])
        s["reviewed"] = True
        changed += 1
    new = []
    for gi, g in enumerate(gaps):
        text = fixes.get(f"G{gi}")
        if not text:
            dropped += 1
            continue
        ws = g["words"]
        words = retime(ws, text.strip(), ws[0]["s"], ws[-1]["e"])
        for w in words:
            w["c"] = 1
        new.append({
            "start": round(words[0]["s"], 2), "end": round(words[-1]["e"], 2),
            "text": " ".join(w["w"] for w in words), "words": words, "added": True,
        })
        added += 1
    segs[:] = [s for s in segs if not s.pop("drop", False)]
    segs.extend(new)
    segs.sort(key=lambda s: s["start"])
    for s in segs:
        s["start"] = round(min(w["s"] for w in s["words"]), 2) if s["words"] else s["start"]
        s["end"] = round(max(w["e"] for w in s["words"]), 2) if s["words"] else s["end"]
    T["reviewed"] = True
    path = os.path.join(d, "transcript.json")
    backup = os.path.join(d, "transcript.whisper.json")
    if not os.path.exists(backup):
        os.replace(path, backup)
    json.dump(T, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    unsure = sum(1 for s in segs for w in s["words"] if w.get("u"))
    print(f"changed {changed} lines, added {added} from gaps, dropped {dropped} gaps/lines, {unsure} words still uncertain")


if __name__ == "__main__":
    cmd, d = sys.argv[1], sys.argv[2]
    if cmd == "prepare":
        n = int(sys.argv[sys.argv.index("--chunks") + 1]) if "--chunks" in sys.argv else 6
        prepare(d, n)
    elif cmd == "apply":
        apply(d, sys.argv[3:])
