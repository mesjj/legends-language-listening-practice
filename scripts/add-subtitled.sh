#!/usr/bin/env bash
# Add a local audio file + its official .srt subtitles (e.g. a Netflix episode) as an episode.
# Subtitles are condensed, not verbatim, so they're used as a reference, not the transcript:
#   1. aligns the subtitles to the audio (gives each subtitle word a time)
#   2. transcribes with whisper.cpp large-v3 + Silero VAD (verbatim but mishears)
#   3. Claude reconciles Whisper vs subtitles line by line (API key, or `claude -p`)
#   4. forced-aligns the final text and flags lines that don't fit their audio
#
# usage: scripts/add-subtitled.sh <audio> <subs.srt> <id> "Episode title" "Show" ["Names for Whisper"]
set -euo pipefail
cd "$(dirname "$0")/.."

AUDIO="$1"; SRT="$2"; ID="$3"; TITLE="$4"; SHOW="$5"; HINT="${6:-$SHOW}"
DIR="media/$ID"
mkdir -p "$DIR"

if [ ! -f "$DIR/audio.mp3" ]; then
  ffmpeg -loglevel error -y -i "$AUDIO" -ac 1 -b:a 96k -codec:a libmp3lame "$DIR/audio.mp3"
  ffmpeg -loglevel error -y -i "$AUDIO" -ar 16000 -ac 1 -c:a pcm_s16le "$DIR/audio16k.wav"
fi
cp "$SRT" "$DIR/subtitles.es.srt"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DIR/audio.mp3" | cut -d. -f1)

# 1. subtitle words with real timings -> subtitles.json3 (the reference for step 3)
if [ ! -f "$DIR/subtitles.json3" ]; then
  python3 -I scripts/srt_to_transcript.py "$DIR/subtitles.es.srt" "$DIR" "$TITLE" --show "$SHOW"
  .venv/bin/python scripts/align.py "$DIR" 2>&1 | grep -v -i warning
  mv "$DIR/transcript.json" "$DIR/transcript.subs.json"
  python3 -I - "$DIR" <<'EOF'
import json, sys
d = sys.argv[1]
T = json.load(open(d + "/transcript.subs.json", encoding="utf-8"))
segs = [{"utf8": w["w"], "tOffsetMs": int(w["s"] * 1000)} for s in T["segments"] for w in s["words"]]
json.dump({"events": [{"tStartMs": 0, "segs": segs}]}, open(d + "/subtitles.json3", "w", encoding="utf-8"), ensure_ascii=False)
EOF
fi

# 2. whisper
if [ ! -f "$DIR/whisper.json" ]; then
  whisper-cli -m models/ggml-large-v3.bin -l es -f "$DIR/audio16k.wav" -ojf -of "$DIR/whisper" \
    --vad -vm models/ggml-silero-v5.1.2.bin -vt 0.1 -vp 400 -vsd 600 -vspd 100 -mc 64 -sns \
    --prompt "$HINT" > "$DIR/whisper.log" 2>&1
fi
if [ ! -f "$DIR/transcript.whisper.json" ]; then
  node scripts/build-transcript.mjs "$DIR/whisper.json" "$DIR/transcript.json" --title "$TITLE" --source "subtitled" --duration "$DUR"
  python3 -I -c "import json,sys; p=sys.argv[1]; T=json.load(open(p)); T['show']=sys.argv[2]; json.dump(T,open(p,'w'),ensure_ascii=False)" "$DIR/transcript.json" "$SHOW"
fi

# 3. reconcile
[ -d "$DIR/review" ] || python3 -I scripts/review_chunks.py prepare "$DIR" --chunks 8
node scripts/correct.mjs "$DIR" --prompt scripts/correction-prompt-subtitles.md
python3 -I scripts/review_chunks.py apply "$DIR" "$DIR"/review/out*.json

# 4. align, then flag lines whose text doesn't fit the audio (they're left out of the games)
.venv/bin/python scripts/align.py "$DIR" 2>&1 | grep -v -i warning
.venv/bin/python scripts/check_lines.py "$DIR" --flag 0.3 2>&1 | grep -v -i warn | tail -1
echo "== done: $DIR"
