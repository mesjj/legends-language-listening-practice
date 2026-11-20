"""Second opinion for lines that don't fit their audio.

For every line whose alignment fit is low, Whisper re-transcribes just that clip. The
forced aligner then scores both versions against the sound and keeps the better one.
Lines that still fit badly are flagged ("flagged": "auto") so the games skip them;
fix or unflag them in the listening view.

Run after align.py (needs the "fit" scores from check_lines.py; it computes them if missing).

usage: .venv/bin/python scripts/recheck_lines.py media/<id> [--below 0.4]
  then: align.py, then check_lines.py --flag 0.3
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
import torch
import torchaudio

sys.path.insert(0, os.path.dirname(__file__))
from align import SR, chars  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Fitter:
    def __init__(self, audio):
        self.audio = audio
        b = torchaudio.pipelines.MMS_FA
        self.dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = b.get_model(with_star=True).to(self.dev).eval()
        self.tok = b.get_tokenizer()
        self.aligner = b.get_aligner()

    def fit(self, start, end, text):
        """Average letter probability of `text` aligned inside [start, end]."""
        keys = [k for k in (chars(w) for w in text.split()) if k]
        if not keys:
            return 0.0
        a, b = max(0, start), min(len(self.audio) / SR, end)
        wav = torch.from_numpy(self.audio[int(a * SR):int(b * SR)]).unsqueeze(0).to(self.dev)
        try:
            with torch.inference_mode():
                em, _ = self.model(wav)
            spans = self.aligner(em.cpu()[0], self.tok(["*"] + keys + ["*"]))[1:-1]
            return float(np.mean([s.score for w in spans for s in w]))
        except Exception:
            return 0.0


def clean(t):
    t = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", t)
    return re.sub(r"\s+", " ", t).strip()


def main(d, below=0.4, flag_below=0.3):
    path = os.path.join(d, "transcript.json")
    T = json.load(open(path, encoding="utf-8"))
    audio, sr = sf.read(os.path.join(d, "audio16k.wav"), dtype="float32")
    assert sr == SR
    F = Fitter(audio)
    segs = T["segments"]

    # windows: from the end of the previous line to the start of the next, capped
    def window(i):
        s = segs[i]
        lo = max(s["start"] - 0.6, segs[i - 1]["end"] - 0.1 if i else 0)
        hi = min(s["end"] + 0.6, segs[i + 1]["start"] + 0.1 if i + 1 < len(segs) else s["end"] + 0.6)
        return min(lo, s["start"]), max(hi, s["end"])

    for i, s in enumerate(segs):
        if "fit" not in s:
            s["fit"] = round(F.fit(s["start"] - 0.15, s["end"] + 0.15, s["text"]), 3)
    todo = [i for i, s in enumerate(segs) if s["fit"] < below and not s.get("edited") and len(s["words"]) >= 2]
    print(f"{len(todo)} of {len(segs)} lines fit below {below}; asking Whisper again", flush=True)

    tmp = tempfile.mkdtemp(prefix="recheck-")
    files = []
    for i in todo:
        a, b = window(i)
        f = os.path.join(tmp, f"{i:05d}.wav")
        sf.write(f, audio[int(a * SR):int(b * SR)], SR)
        files.append(f)
    if files:
        args = ["whisper-cli", "-m", os.path.join(ROOT, "models/ggml-large-v3.bin"), "-l", "es", "-nt", "-otxt"]
        for f in files:
            args += ["-f", f]
        subprocess.run(args, check=True, capture_output=True)

    replaced = 0
    for i in todo:
        s = segs[i]
        txtf = os.path.join(tmp, f"{i:05d}.wav.txt")
        cand = clean(open(txtf, encoding="utf-8").read()) if os.path.exists(txtf) else ""
        a, b = window(i)
        cur = F.fit(a, b, s["text"])
        new = F.fit(a, b, cand) if cand else 0.0
        # Whisper's clip may include a word or two of the neighbours; only take it if it
        # clearly fits better and isn't wildly shorter or longer.
        n_old, n_new = len(s["text"].split()), len(cand.split())
        if cand and new > cur + 0.12 and 0.6 <= n_new / max(1, n_old) <= 1.6:
            s["recheck"] = {"was": s["text"], "fit_was": round(cur, 3), "fit_new": round(new, 3)}
            s["text"] = cand
            toks = cand.split()
            total = sum(len(w) + 1 for w in toks)
            t, words = s["start"], []
            for w in toks:
                dd = (len(w) + 1) / total * (s["end"] - s["start"])
                words.append({"w": w, "s": round(t, 2), "e": round(t + dd, 2)})
                t += dd
            s["words"] = words
            s["fit"] = round(new, 3)
            replaced += 1
            print(f"  #{i} {cur:.2f}→{new:.2f}  {s['recheck']['was']}  ⇒  {cand}")
    print(f"replaced {replaced} lines with Whisper's clip transcription")

    tmpf = path + ".tmp"
    json.dump(T, open(tmpf, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmpf, path)


if __name__ == "__main__":
    argv = sys.argv
    below = float(argv[argv.index("--below") + 1]) if "--below" in argv else 0.4
    main(argv[1], below)
