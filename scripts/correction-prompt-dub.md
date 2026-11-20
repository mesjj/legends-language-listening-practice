You are correcting the transcript of a film dubbed into Latin American Spanish, which an advanced learner will use for listening and shadowing practice. The transcript must be as close to verbatim as possible: exactly what the voice actors say in the dub.

You cannot hear the audio. Each line gives you three things for the same stretch of time:

- `W:` Whisper large-v3, a speech recognizer run on the dubbed audio. **This is the only source of the dub's actual words.** It is close to verbatim (it keeps fillers, repetitions and the dub's own wording), but it mishears: names, foreign words, technical and philosophical terms, overlapping speech, lines under music. Sometimes it garbles a phrase into something that sounds similar but makes no sense, or drops a few words.
- `Y:` the official Spanish subtitles. **They are a separate translation of the original English, not the dub script**, so their wording usually differs from what the actors say ("Elige un color" in Y, "Escoge un color" in the dub). Use Y for the spelling of names and terms, and as a hint to the meaning. Never replace W's wording with Y's just because it differs.
- `E:` the original English subtitles: what the line means. Use it to tell a plausible W from a mishearing (W "persona escocesa" where E says "Irish person" is probably a mishearing of "irlandesa", though dubs do sometimes change details).

Word timings in Y and E are approximate, so a few words may belong to the neighbouring line.

Line format:

    #<id> [start-end] W: <whisper text> | Y: <Spanish subtitle words> | E: <English subtitle words>
    +<id> [start-end] W: (nothing) | Y: <Spanish subtitle words in a gap where Whisper heard nothing> | E: ...

What to do:
- Where W is plausible Spanish that fits the context and the meaning of E, keep W's wording. Fix only its spelling, accents, punctuation, and names or terms you can confirm from Y or E (Lady Gregory, Kierkegaard, Bazin).
- Where W has a word or phrase that is clearly a mishearing (nonsense, or contradicts E in a way a dub wouldn't), replace it with the most likely Spanish the dub actually said: the word that sounds like W's and means what E says. If you can't be confident, wrap your guess in braces: `{palabra}`.
- Where W is garbled beyond repair, give your best reconstruction from W's sounds and E's meaning, with the uncertain words in braces. Don't paste in Y's sentence: it isn't what was said.
- For a `#` line that is a Whisper hallucination (no support in Y or E, repeats nearby text, or a stock phrase like "Gracias." or "Subtítulos por…" over music), output `null` to delete it.
- For `+` gap lines: output `null`. Whisper heard nothing there, and Y is a different translation, so the dub's real words there can't be recovered.

Rules:
- Verbatim, not cleaned up: keep spoken fillers (eh, este, bueno, o sea, ¿no?), false starts and repetitions. Don't fix the speakers' grammar or make the dub's wording more like Y's.
- Standard Spanish orthography with accents and ¿ ¡. Proper nouns as Y or E spell them.
- Keep each line's content within that line; don't move sentences between lines.
- Braces sparingly but honestly: only for a word you're genuinely unsure was said.

Output ONLY a JSON object mapping line ids (without the `#`/`+`) to corrected text, including ONLY lines you changed, and every `+` line (as null). Example:

    {"123": "Bueno, eso es lo que {Kierkegaard} decía.", "G7": null}
