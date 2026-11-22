You are correcting the transcript of an English-language TV episode that will be used by a learner for listening and shadowing practice. The transcript must be as close to verbatim as possible: exactly what the actors say.

You cannot hear the audio. For every line you get two versions of the same stretch of audio:

- `W:` Whisper large-v3, a speech recognizer. It is close to verbatim (keeps fillers, stutters, repetitions, the actual wording) but it mishears words, especially names, made-up words, overlapping speech and lines under music, and it sometimes drops whole lines or garbles them into something that sounds similar but makes no sense.
- `Y:` the official English closed captions of the episode, human-written. Spelling, names, punctuation and meaning are reliable, and captions are closer to verbatim than translated subtitles, but they still drop or trim fillers, stutters and repeated words, and sometimes simplify. Their word timing is approximate, so a word or two may show up on the neighbouring line instead.

Line format:

    #<id> [start-end] W: <whisper text> | Y: <caption words during this line>
    +<id> [start-end] W: (nothing) | Y: <caption words in a gap where Whisper heard nothing>

Decide what was most likely actually said:
- Where W is plausible English that fits the context and agrees with Y in meaning, W's wording is probably what was spoken: keep its extra fillers, stutters and repetitions, but fix its spelling, names and punctuation from Y.
- Where W is garbled, nonsensical or clearly a mishearing, use Y (its words were really said, possibly with a few more that you can't recover).
- Where Y has speech that W missed entirely, include Y's text in that line.
- Interleaved caption words from neighbouring lines (because of timing) are not extra speech; don't duplicate them.

Rules:
- Verbatim, not cleaned up: keep spoken fillers (uh, um, like, y'know), stutters as the captions write them (You-you, I-I), false starts, repetitions, belches written as words only if spoken. Don't fix the speakers' grammar. Keep reduced forms the captions use (gonna, gotta, talkin').
- Spelling: standard English. Proper nouns and invented words as the captions spell them. Write numbers as the captions do.
- For a `#` line that is entirely a Whisper hallucination (no caption support, repeats nearby text or makes no sense, e.g. "Thank you." or "Subtitles by…" over music), output `null` to delete it.
- For `+` gap lines: give the text (normally the caption text, it is real speech), or `null` if it only duplicates a neighbouring line.
- If after weighing both you are still unsure about a specific word, wrap just that word in braces: `{word}`. Use this sparingly but honestly, e.g. for a word only W has that may or may not have been said.
- Keep each line's content within that line; don't move sentences between lines.

Output ONLY a JSON object mapping line ids (without the `#`/`+`) to corrected text, including ONLY lines you changed (and every `+` line, either text or null). Example:

    {"123": "Uh, Morty, come on.", "G7": "Oh, man!", "G8": null}
