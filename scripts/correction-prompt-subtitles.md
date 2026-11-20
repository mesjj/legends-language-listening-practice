You are correcting the transcript of a Spanish-language TV episode (a Colombian comedy series) that will be used by an advanced learner for listening and shadowing practice. The transcript must be as close to verbatim as possible: exactly what the actors say.

You cannot hear the audio. For every line you get two versions of the same stretch of audio:

- `W:` Whisper large-v3, a speech recognizer. It is close to verbatim (keeps fillers, repetitions, the actual wording) but it mishears words, especially names, slang, overlapping speech and lines under music, and it sometimes drops whole lines or garbles them into something that sounds similar but makes no sense ("No me pagues, tu santo" for "En nombre del Padre, Hijo y Espíritu Santo").
- `Y:` the official Spanish subtitles of the episode, human-written. Spelling, names, punctuation and meaning are reliable, but subtitles are condensed for reading speed: they drop fillers, repetitions, interjections and vocatives, and sometimes rephrase ("Debo hacer el almuerzo" when the actor said "Tengo que hacer el almuerzo"). Their word timing is approximate, so a word or two may show up on the neighbouring line instead.

Line format:

    #<id> [start-end] W: <whisper text> | Y: <subtitle words during this line>
    +<id> [start-end] W: (nothing) | Y: <subtitle words in a gap where Whisper heard nothing>

Decide what was most likely actually said:
- Where W is plausible Spanish that fits the context and agrees with Y in meaning, W's wording is probably what was spoken: keep its extra fillers, repetitions and wording, but fix its spelling, names and punctuation from Y.
- Where W is garbled, nonsensical or clearly a mishearing, use Y (its words were really said, possibly with a few more that you can't recover).
- Where Y has speech that W missed entirely, include Y's text in that line.
- Interleaved subtitle words from neighbouring lines (because of timing) are not extra speech; don't duplicate them.

Rules:
- Verbatim, not cleaned up: keep spoken fillers and discourse markers (eh, pues, ¿no?, ¿sí?, o sea, venga), false starts, repetitions. Don't fix the speakers' grammar. Colombian/Bogotá forms such as sumercé, tranquile, parce, berraco are real.
- Spelling: standard Spanish orthography with accents and ¿ ¡. Proper nouns as the subtitles spell them. Write numbers as the subtitles do.
- For a `#` line that is entirely a Whisper hallucination (no subtitle support, repeats nearby text or makes no sense, e.g. "Gracias." or "Subtítulos por…" over music), output `null` to delete it.
- For `+` gap lines: give the text (normally the subtitle text, it is real speech), or `null` if it only duplicates a neighbouring line.
- If after weighing both you are still unsure about a specific word, wrap just that word in braces: `{palabra}`. Use this sparingly but honestly, e.g. for a word only W has that may or may not have been said.
- Keep each line's content within that line; don't move sentences between lines.

Output ONLY a JSON object mapping line ids (without the `#`/`+`) to corrected text, including ONLY lines you changed (and every `+` line, either text or null). Example:

    {"123": "Eh, sumercé, ¿qué más?", "G7": "¡Ay, no!", "G8": null}
