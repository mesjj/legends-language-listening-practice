#!/usr/bin/env bash
# Add a dubbed film (audio in Spanish) with Spanish and English subtitles.
# The Spanish subtitles of a dub are a separate translation, not what the actors say, so here
# Whisper's wording leads; the Spanish subtitles give names and spelling, the English ones the meaning.
#   1. subtitle words, timed by their cues (the subtitles must already be in sync with the audio)
#   2. transcribes with whisper.cpp large-v3 + Silero VAD
#   3. Claude corrects Whisper's mishearings (correction-prompt-dub.md; API key, or `claude -p`),
#      then verify_edits.py re-hears every line Claude changed words in and undoes what the audio contradicts
#   4. forced-aligns the final text and flags lines that don't fit their audio
#
# usage: scripts/add-dubbed.sh <video or audio> <subs.es.srt> <subs.en.srt | -> <id> "Title" "Show" ["Names for Whisper"] [chunks]
#   Pass - for the English subtitles when there are none (Claude then corrects without the meaning guide).
set -euo pipefail
cd "$(dirname "$0")/.."

AUDIO="$1"; SRT="$2"; SRT_EN="$3"; ID="$4"; TITLE="$5"; SHOW="$6"; HINT="${7:-$SHOW}"; CHUNKS="${8:-16}"
DIR="media/$ID"
mkdir -p "$DIR"

if [ ! -f "$DIR/audio.mp3" ]; then
  ffmpeg -loglevel error -y -i "$AUDIO" -vn -ac 1 -b:a 96k -codec:a libmp3lame "$DIR/audio.mp3"
  ffmpeg -loglevel error -y -i "$AUDIO" -vn -ar 16000 -ac 1 -c:a pcm_s16le "$DIR/audio16k.wav"
fi
cp "$SRT" "$DIR/subtitles.es.srt"
[ "$SRT_EN" = "-" ] || cp "$SRT_EN" "$DIR/subtitles.en.srt"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DIR/audio.mp3" | cut -d. -f1)

# 1. subtitle words timed by their cues -> subtitles.json3, subtitles.en.json3 (and transcript.subs.json
#    for the Netflix / Whisper comparison panel). No forced alignment: the dub doesn't say these words.
if [ ! -f "$DIR/subtitles.json3" ]; then
  if [ -f "$DIR/subtitles.en.srt" ]; then
    python3 -I scripts/srt_to_transcript.py "$DIR/subtitles.en.srt" "$DIR" "$TITLE"
    mv "$DIR/transcript.json" "$DIR/transcript.subs.en.json"
  fi
  python3 -I scripts/srt_to_transcript.py "$DIR/subtitles.es.srt" "$DIR" "$TITLE" --show "$SHOW"
  mv "$DIR/transcript.json" "$DIR/transcript.subs.json"
  python3 -I - "$DIR" <<'EOF'
import json, sys
d = sys.argv[1]
import os
for src, dst in (("transcript.subs.json", "subtitles.json3"), ("transcript.subs.en.json", "subtitles.en.json3")):
    if not os.path.exists(f"{d}/{src}"): continue
    T = json.load(open(f"{d}/{src}", encoding="utf-8"))
    segs = [{"utf8": w["w"], "tOffsetMs": int(w["s"] * 1000)} for s in T["segments"] for w in s["words"]]
    json.dump({"events": [{"tStartMs": 0, "segs": segs}]}, open(f"{d}/{dst}", "w", encoding="utf-8"), ensure_ascii=False)
EOF
fi

# 2. whisper
if [ ! -f "$DIR/whisper.json" ]; then
  whisper-cli -m models/ggml-large-v3.bin -l es -f "$DIR/audio16k.wav" -ojf -of "$DIR/whisper" \
    --vad -vm models/ggml-silero-v5.1.2.bin -vt 0.1 -vp 400 -vsd 600 -vspd 100 -mc 0 -sns \
    --prompt "$HINT" > "$DIR/whisper.log" 2>&1
fi
# On a long film, Whisper fed its own text (-mc 64) got stuck repeating one line for an hour;
# -mc 0 avoids that. Stop here if it happens anyway, rather than have Claude delete the lot.
python3 -I - "$DIR/whisper.json" <<'EOF'
import json, sys
segs = json.load(open(sys.argv[1], encoding="utf-8"))["transcription"]
run = 0
for a, b in zip(segs, segs[1:]):
    run = run + 1 if a["text"].strip() == b["text"].strip() else 0
    if run >= 8:
        sys.exit(f"Whisper is looping at {b['timestamps']['from']}: \"{b['text'].strip()}\" over and over. Re-run that stretch.")
EOF
if [ ! -f "$DIR/transcript.whisper.json" ] && [ ! -f "$DIR/transcript.json" ]; then
  node scripts/build-transcript.mjs "$DIR/whisper.json" "$DIR/transcript.json" --title "$TITLE" --source "dubbed" --duration "$DUR"
  python3 -I -c "import json,sys; p=sys.argv[1]; T=json.load(open(p)); T['show']=sys.argv[2]; json.dump(T,open(p,'w'),ensure_ascii=False)" "$DIR/transcript.json" "$SHOW"
fi

# 3. correct
[ -d "$DIR/review" ] || python3 -I scripts/review_chunks.py prepare "$DIR" --chunks "$CHUNKS"
node scripts/correct.mjs "$DIR" --prompt scripts/correction-prompt-dub.md
# a second hearing for the words Claude changed (it can lean on the English over the audio)
python3 -I scripts/verify_edits.py "$DIR" "$HINT"
python3 -I scripts/review_chunks.py apply "$DIR" "$DIR"/review/out*.json

# 4. align, then flag lines whose text doesn't fit the audio (they're left out of the games)
.venv/bin/python scripts/align.py "$DIR" 2>&1 | grep -v -i warning
.venv/bin/python scripts/check_lines.py "$DIR" --flag 0.3 2>&1 | grep -v -i warn | tail -1
echo "== done: $DIR"
