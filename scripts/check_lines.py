"""Score how well each transcript line matches its audio, and flag the bad ones.

Uses the same MMS forced aligner as align.py: for each line it reports the average
probability the acoustic model gives to the line's letters where they were placed.
Lines whose text isn't what's said (subtitle paraphrase, a mishearing) score low.

usage:
  .venv/bin/python scripts/check_lines.py media/<id>              # report only
  .venv/bin/python scripts/check_lines.py media/<id> --flag 0.45  # flag lines below 0.45
Writes a per-line "fit" score into transcript.json either way (so the app can show it).
Flags are {"flagged": "auto"} so they're distinguishable from ones you set by hand.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
import torch
import torchaudio

sys.path.insert(0, os.path.dirname(__file__))
from align import SR, chars  # noqa: E402


def main(d, threshold=None):
    path = os.path.join(d, "transcript.json")
    T = json.load(open(path, encoding="utf-8"))
    audio, sr = sf.read(os.path.join(d, "audio16k.wav"), dtype="float32")
    assert sr == SR
    bundle = torchaudio.pipelines.MMS_FA
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = bundle.get_model(with_star=True).to(dev).eval()
    tokenizer = bundle.get_tokenizer()
    aligner = bundle.get_aligner()

    scores = []
    for si, seg in enumerate(T["segments"]):
        keys = [k for k in (chars(w["w"]) for w in seg["words"]) if k]
        if not keys:
            continue
        a = max(0, seg["start"] - 0.15)
        b = min(len(audio) / SR, seg["end"] + 0.15)
        wav = torch.from_numpy(audio[int(a * SR):int(b * SR)]).unsqueeze(0).to(dev)
        try:
            with torch.inference_mode():
                em, _ = model(wav)
            em = em.cpu()
            spans = aligner(em[0], tokenizer(["*"] + keys + ["*"]))[1:-1]
            # average letter probability over the line
            probs = [s.score for word in spans for s in word]
            fit = float(np.mean(probs))
        except Exception:
            fit = 0.0
        seg["fit"] = round(fit, 3)
        scores.append((fit, si))

    fits = np.array([f for f, _ in scores])
    print(f"{len(fits)} lines · median fit {np.median(fits):.2f} · "
          f"p10 {np.percentile(fits, 10):.2f} · p5 {np.percentile(fits, 5):.2f}")
    worst = sorted(scores)[:25]
    for f, si in worst:
        s = T["segments"][si]
        print(f"  {f:.2f}  #{si} [{int(s['start'] // 60)}:{s['start'] % 60:04.1f}] {s['text']}")

    if threshold is not None:
        n = 0
        for f, si in scores:
            seg = T["segments"][si]
            if f < threshold and not seg.get("edited") and not seg.get("flagged"):
                seg["flagged"] = "auto"
                n += 1
            elif f >= threshold and seg.get("flagged") == "auto":
                del seg["flagged"]
        print(f"flagged {n} lines below {threshold}")
    tmp = path + ".tmp"
    json.dump(T, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, path)


if __name__ == "__main__":
    th = float(sys.argv[sys.argv.index("--flag") + 1]) if "--flag" in sys.argv else None
    main(sys.argv[1], th)
