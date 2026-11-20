"""A second hearing for the words Claude changed in a dub's transcript.

Claude sees the English subtitles, so it sometimes "fixes" what the dub really says to match them
(the dub says "escocesa", the English says "Irish"). For every line where Claude changed words,
this transcribes that clip again on its own (whisper-server) and, for each changed stretch:
- keeps Claude's words if the clip agrees with them;
- keeps them too if they sound like Whisper's (a spelling or grammar fix: Quiere -> Quiero) or are a
  name the subtitles spell (Trifo -> Truffaut): the same model would mishear those the same way again;
- reverts to Whisper's words if the clip agrees with Whisper and not with Claude;
- otherwise keeps Claude's words wrapped in {braces} (shown as uncertain).
Rewrites review/out*.json in place; Claude's originals are kept in review/claude-orig/.

usage: python3 -I scripts/verify_edits.py media/<id> ["Names for Whisper"]
needs whisper-server on 127.0.0.1:$WHISPER_PORT (8791); starts one if none is running."""
import difflib, glob, json, os, re, shutil, subprocess, sys, unicodedata, urllib.request, uuid
import time
D = sys.argv[1]
HINT = sys.argv[2] if len(sys.argv) > 2 else ""
PORT = os.environ.get("WHISPER_PORT", "8791")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def up():
    try: urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=3); return True
    except Exception: return False
if not up():
    subprocess.Popen([os.environ.get("WHISPER_SERVER_BIN", "whisper-server"), "-m", os.path.join(ROOT, "models/ggml-large-v3.bin"),
                      "--host", "127.0.0.1", "--port", PORT, "-l", "es"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        if up(): break
        time.sleep(1)
def norm(t):
    t = unicodedata.normalize("NFD", t.lower().replace("{", "").replace("}", ""))
    return "".join(c for c in t if unicodedata.category(c) != "Mn" and (c.isalnum()))
def hear(a, b):
    wav = f"{D}/review/clip_{uuid.uuid4().hex}.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(max(0, a - 0.3)), "-to", str(b + 0.3), "-i", f"{D}/audio16k.wav", wav], check=True)
    body, bnd = [], uuid.uuid4().hex
    def field(n, v): body.extend([f"--{bnd}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n".encode(), v.encode(), b"\r\n"])
    field("language", "es"); field("response_format", "json"); field("prompt", HINT); field("temperature", "0")
    body.extend([f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode(), open(wav, "rb").read(), f"\r\n--{bnd}--\r\n".encode()])
    os.remove(wav)
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/inference", data=b"".join(body), headers={"Content-Type": f"multipart/form-data; boundary={bnd}"})
    return json.load(urllib.request.urlopen(req, timeout=120))["text"]
# how a stretch sounds, roughly, in Spanish: spelling fixes sound the same and are kept
def sound(t):
    t = norm(t).replace("qu", "k").replace("ll", "y").replace("h", "").replace("v", "b").replace("z", "s").replace("x", "ks").replace("w", "u")
    t = re.sub(r"c([eiéí])", r"s\1", t); t = re.sub(r"g([ei])", r"j\1", t); t = t.replace("c", "k")
    return t
def alike(a, b):
    a, b = sound(a), sound(b)
    return bool(a or b) and difflib.SequenceMatcher(None, a, b).ratio() >= 0.7
subs = "".join(open(f"{D}/{n}", encoding="utf-8").read() for n in ("subtitles.es.srt", "subtitles.en.srt") if os.path.exists(f"{D}/{n}"))
def subname(toks):  # a capitalised word the subtitles also have: a name, keep Claude's spelling
    return any(re.sub(r"[^\w]", "", t)[:1].isupper() and len(re.sub(r"[^\w]", "", t)) > 2 and re.sub(r"[^\w]", "", t) in subs for t in toks)
# the pre-review transcript the chunk ids refer to (transcript.json until review_chunks.py apply backs it up)
W_SRC = f"{D}/transcript.whisper.json" if os.path.exists(f"{D}/transcript.whisper.json") else f"{D}/transcript.json"
W = json.load(open(W_SRC, encoding="utf-8"))["segments"]
files = sorted(glob.glob(f"{D}/review/out*.json"))
os.makedirs(f"{D}/review/claude-orig", exist_ok=True)
stats = {"keep": 0, "revert": 0, "brace": 0, "spelling": 0}
log = []
for f in files:
    keep = f"{D}/review/claude-orig/{os.path.basename(f)}"
    if not os.path.exists(keep): shutil.copy(f, keep)
    fx = json.load(open(keep, encoding="utf-8"))
    for k, v in fx.items():
        if k.startswith("G") or v is None: continue
        w = W[int(k)]
        wt, ct = w["text"].split(), v.split()
        A, B = [norm(t) for t in wt], [norm(t) for t in ct]
        if [a for a in A if a] == [b for b in B if b]: continue
        I = " ".join(norm(t) for t in hear(w["start"], w["end"]).split())
        out = []
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal" or not ("".join(A[i1:i2]) or "".join(B[j1:j2])):
                out += ct[j1:j2]; continue
            # the stretch with a word of context either side, as heard alone
            ctxW = " ".join(x for x in A[max(0, i1 - 1):i2 + 1] if x)
            ctxC = " ".join(x for x in B[max(0, j1 - 1):j2 + 1] if x)
            inW, inC = ctxW in I, ctxC in I
            if inC and not inW: out += ct[j1:j2]; stats["keep"] += 1; kind = "keep"
            elif alike(" ".join(wt[i1:i2]), " ".join(ct[j1:j2])) or subname(ct[j1:j2]): out += ct[j1:j2]; stats["spelling"] += 1; kind = "spelling"
            elif inW and not inC: out += wt[i1:i2]; stats["revert"] += 1; kind = "revert"
            else:
                out += [t if "{" in t or not norm(t) else "{" + t + "}" for t in ct[j1:j2]]; stats["brace"] += 1; kind = "brace"
            log.append(f"#{k} {kind}: W «{' '.join(wt[i1:i2])}» C «{' '.join(ct[j1:j2])}» | alone: {I[:120]}")
        fx[k] = " ".join(out)
    json.dump(fx, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(f"{D}/review/verify.log", "w").write("\n".join(log))
print(stats)
