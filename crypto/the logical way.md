# The Logical Way

> *A Vulcan has left their final message to the world before dying. They had spent centuries thinking of nothing but logic. Can you uncover their final message?*
> Format: `spooky{hello_world}`

I was provided with a 7-Zip archive called `My_Message_to_you.7z`.

## Cracking the archive

`7z l` / `py7zr` showed the archive was **AES-256 encrypted**, but the header itself was *not* encrypted, so I could still read the metadata: a single payload named `My Message to you.zip`. No comment, no stego-looking tail, nothing to pull without the password.

There were no cracking tools or wordlists on my machine, and a pure-Python dictionary attack against AES-256 is painfully slow — a strong hint the password wasn't meant to be brute-forced but **deduced from the riddle**.

The line *"nothing but logic"* turned out to be literal. After striking out on the obvious Star Trek guesses (`spock`, `vulcan`, `surak`, `LLAP`, `live long and prosper`, …), I permuted the core stems by case and the all-caps form hit:

```
password = LOGIC
```

Extracting gave `My Message to you.zip`, and inside that, `LOGIC.pdf`.

## The PDF

The PDF was 2 pages of ornate **Vulcan calligraphy**. `pdftotext` / text extraction returned nothing useful — because the real text layer was just invisible whitespace. The visible glyphs were ~177 vector drawings (103 on page 1, 74 on page 2), one glyph per character.

So this was a **monoalphabetic substitution cipher** written in a Vulcan font, with the English spaces dropped.

## Recovering the cipher

I rendered each glyph's bounding box to pixels, normalized it, and clustered by visual (Hamming) distance:

- **21 distinct glyph shapes** → a clean 21-symbol alphabet.
- One long run of symbols repeated near the start → a refrain, confirming the clustering was stable.

```python
# render each glyph bbox, normalize to 24x48, cluster by hamming distance < 0.12
# -> 21 distinct symbols, emitted as an integer sequence
```

## Solving the substitution

A word-list model was too weak for spaceless text, so I pulled a 6.5 MB running-English corpus (Norvig's `big.txt`) and built a **quadgram log-probability model**, then ran a hill-climbing solver (random restarts + pairwise key swaps).

It converged almost immediately on readable English:

```
thosewhodonotfollowtheprinciplesofvulcanlogicwillfail
vtosh?aturnira?donotpity
thosewhodonotfollowlogichelpthemseereason
turnthevulcanintoenglishandwrapitwithunderscorestoseereason
```

Two anchors pinned the alphabet with certainty, e.g. `follow` = `8,2,9,9,2,5` → `f,o,l,l,o,w` and `principles` = `10,11,12,7,13,12,10,9,4,3`.

## Two loose ends

**Word boundaries.** Spaces had been stripped from the text layer — but they were still encoded in the **glyph spacing**. Normal glyph pitch was ~33px; a ~44px gap marked a space. Reading pitch per row recovered every word break.

**Three rare glyphs.** Two symbols appeared *only* in the gibberish middle `vtosh ?atur nira?` (plus a `y` used once in `pity`). Statistics couldn't fix them, but the phrase was the giveaway: `vtosh katur` is **`V'tosh ka'tur`** — canonical Star Trek Vulcan for *"Vulcans without logic"* (ENT: "Fusion"), the ones who rejected Surak's path. That fixed the unknown glyph as `k`.

## The decoded message

> *Those who do not follow the principles of Vulcan logic will fail.* ***vtosh katur nirak.*** *Do not pity those who do not follow logic — help them see reason. Turn the Vulcan into English and wrap it with underscores to see reason.*

The message literally describes how to build the flag: take **the Vulcan** (the transliterated Vulcan-language phrase `vtosh katur nirak`) and **wrap it with underscores**.

🚩

```flag
spooky{vtosh_katur_nirak}
```
