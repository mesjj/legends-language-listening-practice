"""Forced-align transcript words to the audio (torchaudio MMS_FA, wav2vec2).

Whisper's own word timings are rough (often zero-length words). Given the final
text, this finds exactly where each word is spoken, line by line, so selecting
and looping a short phrase is precise. Keeps every other field in transcript.json.

usage: .venv/bin/python scripts/align.py media/<id>
"""
import json
import os
import re
import sys
import unicodedata

import numpy as np
import soundfile as sf
import torch
import torchaudio

SR = 16000
PAD = 0.45  # seconds of audio either side of a line


def chars(word):
    w = unicodedata.normalize("NFD", word.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z']", "", w)


def split_long(seg, max_words=30):
    """Split an over-long line at sentence ends (now that word timings are good)."""
    words = seg["words"]
    if len(words) <= max_words:
        return [seg]
    parts, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        left = len(words) - i - 1
        if re.search(r"[.?!…]$", w["w"]) and len(cur) >= 6 and left >= 4:
            parts.append(cur)
            cur = []
    if cur:
        parts.append(cur)
    out = []
    for p in parts:
        s = {k: v for k, v in seg.items() if k not in ("words", "text", "start", "end")}
        s.update(words=p, text=" ".join(w["w"] for w in p), start=p[0]["s"], end=p[-1]["e"])
        out.append(s)
    return out


def main(d):
    path = os.path.join(d, "transcript.json")
    T = json.load(open(path, encoding="utf-8"))
    audio, sr = sf.read(os.path.join(d, "audio16k.wav"), dtype="float32")
    assert sr == SR

    bundle = torchaudio.pipelines.MMS_FA
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = bundle.get_model(with_star=True).to(dev).eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()

    segs = T["segments"]
    ok = failed = 0
    for si, seg in enumerate(segs):
        words = seg["words"]
        keys = [chars(w["w"]) for w in words]
        idx = [i for i, k in enumerate(keys) if k]
        if not idx:
            continue
        lo_lim = segs[si - 1]["start"] if si > 0 else 0
        hi_lim = segs[si + 1]["end"] if si + 1 < len(segs) else len(audio) / SR
        for pad in (PAD, 1.5):
            a = max(lo_lim, seg["start"] - pad, 0)
            b = min(hi_lim, seg["end"] + pad, len(audio) / SR)
            wav = torch.from_numpy(audio[int(a * SR):int(b * SR)]).unsqueeze(0).to(dev)
            try:
                with torch.inference_mode():
                    em, _ = model(wav)
                em = em.cpu()
                # "*" soaks up neighbouring speech inside the padding
                spans = aligner(em[0], tokenizer(["*"] + [keys[i] for i in idx] + ["*"]))[1:-1]
            except Exception:
                continue
            ratio = (b - a) / em.size(1)
            for i, sp in zip(idx, spans):
                words[i]["s"] = round(a + sp[0].start * ratio, 2)
                words[i]["e"] = round(a + sp[-1].end * ratio, 2)
            break
        else:
            failed += 1
            continue
        ok += 1
        # words with no letters (numbers, symbols): place them between neighbours
        for i, k in enumerate(keys):
            if not k:
                prev_e = words[i - 1]["e"] if i > 0 else seg["start"]
                nxt = next((words[j]["s"] for j in range(i + 1, len(words)) if keys[j]), prev_e + 0.4)
                words[i]["s"], words[i]["e"] = round(prev_e, 2), round(max(prev_e, nxt), 2)
        # stretch each word to the next word's start so highlighting has no gaps
        for i in range(len(words) - 1):
            gap = words[i + 1]["s"] - words[i]["e"]
            if 0 < gap < 0.25:
                words[i]["e"] = words[i + 1]["s"]
        seg["start"] = words[0]["s"]
        seg["end"] = words[-1]["e"]
        if si % 100 == 0:
            print(f"  {si}/{len(segs)}", flush=True)

    segs.sort(key=lambda s: s["start"])
    T["segments"] = [part for s in segs for part in split_long(s)]
    T["aligned"] = True
    tmp = path + ".tmp"
    json.dump(T, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)
    print(f"aligned {ok} lines, {failed} kept their old timing")


if __name__ == "__main__":
    main(sys.argv[1])
