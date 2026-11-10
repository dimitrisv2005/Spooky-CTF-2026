# Phasmophobia

I was given an audio file `PhasmophobiaChallenge.wav` and a portrait
`ebersecret.png`. The story went on about Eberhardt Hall being haunted — eerie
haunted-house music, something *whispering*, a *portrait that shifted*, and a
*ghost wearing a laurel*. The hints spelled out two things: the vivid
storytelling was supposed to point at the method, and the flag is in **two
parts** — the first in the audio, the second in the PNG.

## Reading the clues

A *ghost wearing a laurel* and a *portrait that shifts*: Julius Caesar wore a
laurel wreath, and a "shift" is exactly what a Caesar cipher does. So both
halves are going to be Caesar-shifted text.

## Part 1 — the whispers (audio)

"Whispering" that you can't quite make out is the classic tell for text drawn
into a **spectrogram**. I rendered the spectrogram of the wav and zoomed into
the band where the writing sat (roughly 7–15 s, ~8–11 kHz):

```python
import wave, numpy as np
import matplotlib.pyplot as plt

w = wave.open("PhasmophobiaChallenge.wav")
d = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, 2).astype(float)
s = d[:, 0] + d[:, 1]                      # mix the two channels

plt.specgram(s, NFFT=2048, Fs=44100, noverlap=1792, cmap="gray")
plt.ylim(8000, 11000)
plt.show()
```

The text reads (roughly) `WWWOIJWWOIJWWOIJWWaxwwxml`. Applying a Caesar shift of
**18** (`W → O`) gives the first half:

```
OOOGABOOGABOOGABOOspooped
```

## Part 2 — the portrait (PNG)

The second half is hidden in the **least-significant bits** of the portrait's
RGB pixels, behind a small length prefix:

```python
from PIL import Image
import numpy as np

a = np.array(Image.open("ebersecret.png"))
bits = (a[..., :3] & 1).reshape(-1)        # LSB of R, G, B in row order
data = np.packbits(bits).tobytes()
print(data[:48])                           # length prefix + hidden ASCII
```

The recovered text is `JWWowbgwc`, decorated with a hint — `(18 salads.
yummers)`, i.e. a *Caesar salad* with shift **18** — and `(2)` marking it as
part two. Shift 18 on `JWWowbgwc` gives:

```
BOOgotyou
```

## Helper + result

```python
def caesar(s, k=18):
    out = ""
    for c in s:
        if   c.isupper(): out += chr((ord(c) - 65 + k) % 26 + 65)
        elif c.islower(): out += chr((ord(c) - 97 + k) % 26 + 97)
        else:             out += c
    return out
```

Stitched together it reads "Ooga booga booga boo, spooped! BOO, got you." 🚩

```flag
spooky{OOOGABOOGABOOGABOOspoopedBOOgotyou}
```
