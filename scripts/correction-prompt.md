You are correcting the transcript of a Spanish-language audio recording (an informal Colombian talk show / interview / podcast) that will be used by an advanced learner for listening practice. The transcript must be as close to verbatim as possible.

You cannot hear the audio. For every line you get two independent machine transcriptions of the same stretch of audio:

- `W:` Whisper large-v3. Usually better punctuation, proper nouns and full sentences, but it sometimes drops short interjections, crosstalk and fast asides, and occasionally hallucinates or repeats a phrase.
- `Y:` YouTube's automatic captions. No reliable punctuation, misspells names, but often catches short words and interjections Whisper skipped. `__` means a censored swear word, never output `__`. Its word timing is approximate, so a word or two may show up on the neighbouring line instead.

Line format:

    #<id> [start-end] W: <whisper text> | Y: <youtube words heard during this line>
    +<id> [start-end] W: (nothing) | Y: <words only YouTube heard, in a gap between Whisper lines>

Decide what was most likely actually said, using both versions, the surrounding conversation, and your knowledge of colloquial Colombian Spanish (parce, marica/marica, qué más, o sea, pues, ¿sí o qué?, berraco, chimba, guaro, etc.).

Rules:
- Verbatim, not cleaned up: keep fillers and discourse markers that were spoken (o sea, eh, pues, ¿no?, ¿sí?, marica), false starts, repetitions, swearing. Do not fix the speakers' grammar.
- Where the versions agree, keep it. Where they differ, choose or merge. Add words YouTube heard that Whisper dropped if they plausibly were spoken. Remove Whisper hallucinations (text that doesn't fit and YouTube doesn't support, repeated phrases).
- Spelling: standard Spanish orthography with accents and ¿ ¡. Proper nouns spelled correctly (people, brands, places, songs, telenovelas). The host is Juanpis González (character played by Alejandro Riaño) and the show is "The Juanpis Live Show".
- For a `#` line that is entirely a Whisper hallucination (YouTube heard nothing like it there, and it repeats nearby text or makes no sense), output `null` to delete it.
- For `+` gap lines: give the text if it is real speech, or `null` to drop it (noise, laughter, music, applause, duplicates of a neighbouring line).
- If after weighing both you are still unsure about a specific word, wrap just that word in braces: `{palabra}`. Use this sparingly but honestly.
- Keep each line's content within that line; don't move sentences between lines.

Output ONLY a JSON object mapping line ids (without the `#`/`+`) to corrected text, including ONLY lines you changed (and every `+` line, either text or null). Example:

    {"123": "O sea, ¿qué más, parce?", "G7": "¡Uy, no!", "G8": null}
