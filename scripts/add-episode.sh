#!/usr/bin/env bash
# Add a YouTube video (or any yt-dlp URL) as an episode:
#   1. downloads audio + YouTube's auto-captions
#   2. transcribes with whisper.cpp large-v3 + Silero VAD -> media/<id>/transcript.json
#   3. Claude reconciles Whisper vs YouTube line by line (API key, or `claude -p`)
#   4. forced-aligns every word to the audio (torchaudio MMS) for precise timings
#
# usage: scripts/add-episode.sh <url> ["Names, places, show title to bias spelling"]
# needs: yt-dlp, ffmpeg, whisper-cli (brew install whisper-cpp), node,
#        models/ggml-large-v3.bin and models/ggml-silero-v5.1.2.bin
set -euo pipefail
cd "$(dirname "$0")/.."

URL="$1"
HINT="${2:-}"
ID=$(yt-dlp --skip-download --print id "$URL" 2>/dev/null)
TITLE=$(yt-dlp --skip-download --print title "$URL" 2>/dev/null)
DIR="media/$ID"
mkdir -p "$DIR"
echo "== $ID: $TITLE"

if [ ! -f "$DIR/audio.mp3" ]; then
  yt-dlp -q -f bestaudio -o "$DIR/source.%(ext)s" "$URL"
  SRC=$(ls "$DIR"/source.* | head -1)
  # Constant-bitrate mono mp3 so browsers seek precisely (VBR seeking drifts).
  ffmpeg -loglevel error -y -i "$SRC" -ac 1 -b:a 96k -codec:a libmp3lame "$DIR/audio.mp3"
  ffmpeg -loglevel error -y -i "$SRC" -ar 16000 -ac 1 -c:a pcm_s16le "$DIR/audio16k.wav"
  rm -f "$SRC"
fi
if ! ls "$DIR"/audio.es*.json3 >/dev/null 2>&1; then
  yt-dlp -q --skip-download --write-auto-subs --sub-langs es-orig,es --sub-format json3 -o "$DIR/audio" "$URL" || true
  [ -f "$DIR/audio.es.json3" ] && [ ! -f "$DIR/audio.es-orig.json3" ] && mv "$DIR/audio.es.json3" "$DIR/audio.es-orig.json3"
fi

PROMPT_ARGS=()
[ -n "$HINT" ] && PROMPT_ARGS=(--prompt "$HINT")

if [ ! -f "$DIR/whisper.json" ]; then
  whisper-cli -m models/ggml-large-v3.bin -l es -f "$DIR/audio16k.wav" -ojf -of "$DIR/whisper" \
    --vad -vm models/ggml-silero-v5.1.2.bin -vt 0.1 -vp 400 -vsd 600 -vspd 100 -mc 64 -sns \
    ${PROMPT_ARGS[@]+"${PROMPT_ARGS[@]}"} > "$DIR/whisper.log" 2>&1
fi

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$DIR/audio.mp3")
node scripts/build-transcript.mjs "$DIR/whisper.json" "$DIR/transcript.json" \
  --title "$TITLE" --source "$URL" --duration "$DUR"
if [ -f "$DIR/audio.es-orig.json3" ]; then
  echo "== Claude correction pass"
  python3 -I scripts/review_chunks.py prepare "$DIR" --chunks 6
  node scripts/correct.mjs "$DIR"
  python3 -I scripts/review_chunks.py apply "$DIR" "$DIR"/review/out*.json
else
  echo "== skipping correction pass (no YouTube captions)"
fi

echo "== aligning words to audio"
.venv/bin/python scripts/align.py "$DIR" 2>&1 | grep -v -i warning
# 5. the non-Spanish proper names, which the games don't count when they're wrong
node scripts/find_names.mjs "$DIR" || echo "(names skipped)"
echo "== done: open the app and pick \"$TITLE\""
