"""Cross-check a transcript.json against YouTube auto-captions (json3).

Two independent recognisers rarely make the same mistake, so words where they
agree are very likely right. Words where they disagree (or where whisper's own
token confidence is low) get "u": 1 in transcript.json so the app can flag them,
and the disagreements are written to a review file.

usage: python3 -I scripts/crosscheck.py media/<id>/transcript.json media/<id>/audio.es-orig.json3 \
          [--whisper media/<id>/whisper.json] [--review review.txt]
"""
import difflib
import json
import re
import sys
import unicodedata


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]", "", w)


def yt_words(path):
    d = json.load(open(path, encoding="utf-8"))
    out = []
    for ev in d.get("events", []):
        if "segs" not in ev:
            continue
        t0 = ev.get("tStartMs", 0)
        for s in ev["segs"]:
            for piece in s.get("utf8", "").split():
                if piece.startswith("[") and piece.endswith("]"):
                    continue  # [música], [aplausos]
                n = norm(piece)
                if n:
                    out.append((n, piece, (t0 + s.get("tOffsetMs", 0)) / 1000))
    return out


def main():
    args = sys.argv[1:]
    tpath, ypath = args[0], args[1]
    opt = dict(zip(args[2::2], args[3::2]))
    T = json.load(open(tpath, encoding="utf-8"))

    # flat list of transcript words
    flat = []
    for si, seg in enumerate(T["segments"]):
        for wi, w in enumerate(seg["words"]):
            w.pop("u", None)
            flat.append((si, wi, w))
    A = [norm(w["w"]) for _, _, w in flat]
    Y = yt_words(ypath)
    B = [y[0] for y in Y]

    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    regions = []
    agree = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            agree += i2 - i1
            continue
        mine = [flat[k][2]["w"] for k in range(i1, i2)]
        theirs = [Y[k][1] for k in range(j1, j2)]
        # ignore pure filler differences
        if op == "delete" and all(norm(m) in {"eh", "ah", "mm", "o", "y", "ay", "uy", "eso"} for m in mine):
            continue
        for k in range(i1, i2):
            flat[k][2]["u"] = 1
        if op == "insert" and i1 > 0:
            flat[i1 - 1][2]["u"] = 1  # youtube heard something here we don't have
        t = flat[min(i1, len(flat) - 1)][2]["s"]
        regions.append((t, op, " ".join(mine), " ".join(theirs), flat[min(i1, len(flat) - 1)][0]))

    # low-confidence tokens from whisper (optional)
    if "--whisper" in opt:
        W = json.load(open(opt["--whisper"], encoding="utf-8"))
        lowp = []
        for seg in W["transcription"]:
            word, ps = "", []
            for tok in seg["tokens"]:
                txt = tok["text"]
                if txt.startswith("[_") or txt.startswith("["):
                    continue
                if txt.startswith(" ") and word:
                    lowp.append((norm(word), min(ps)))
                    word, ps = "", []
                word += txt.strip()
                ps.append(tok.get("p", 1))
            if word:
                lowp.append((norm(word), min(ps)))
        # whisper words map 1:1 onto transcript words when the norms line up
        sm2 = difflib.SequenceMatcher(None, A, [w for w, _ in lowp], autojunk=False)
        for op, i1, i2, j1, j2 in sm2.get_opcodes():
            if op == "equal":
                for k in range(i2 - i1):
                    if lowp[j1 + k][1] < 0.35:
                        flat[i1 + k][2]["u"] = 1

    json.dump(T, open(tpath, "w", encoding="utf-8"), ensure_ascii=False)
    flagged = sum(1 for _, _, w in flat if w.get("u"))
    print(f"{len(A)} words, {agree} agree with YouTube ({agree / max(1, len(A)):.1%}); "
          f"{len(regions)} disagreement regions; {flagged} words flagged")

    if "--review" in opt:
        with open(opt["--review"], "w", encoding="utf-8") as f:
            for t, op, mine, theirs, si in regions:
                m, s = divmod(int(t), 60)
                f.write(f"[{si}] {m}:{s:02d}\t{op}\tW: {mine}\tY: {theirs}\n")


main()
