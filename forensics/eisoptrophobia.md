# Eisoptrophobia

I was given a dark photo of a woman looking into a bathroom mirror. Her reflection looks slightly off, and there are red streaks across the glass. The challenge text:

> Something strange is happening in the mirror. What appears to be an ordinary reflection may be hiding something more than meets the eye. Look closely, investigate the image, and uncover what lies beneath the surface.

## Initial Attempts

The red marks on the mirror were the first thing I noticed, and I wondered whether they spelled something or pointed somewhere. They turned out to be decoration only.

## Standard Forensics

I went through the checklist again:

- `file`: a normal PNG
- PNG chunks: no `tEXt`/`iTXt`/`zTXt` metadata and **nothing after `IEND`**, so no appended ZIP like in the logo challenge
- `strings`: nothing

With the file structure clean, whatever was hidden had to be inside the pixel values.

## Finding the solution

In the Haunted Portrait challenge, the message was drawn as a picture in one bit plane. This time I read the least significant bits as **data**. Each pixel has R, G and B values from 0 to 255. Changing only the last bit of each value moves it by at most 1, which the eye can't see.

I took the lowest bit of every value in order (R, G, B of pixel 1, then pixel 2, and so on, row by row) and grouped the bits into bytes:

```python
from PIL import Image
import numpy as np, base64

a = np.array(Image.open('mirror.png').convert('RGB'))
data = np.packbits((a & 1).reshape(-1)[:352]).tobytes()   # 44 chars × 8 bits
print(data)
```

The first bytes were readable text, followed by random noise (the photo's natural bits):

```
c3Bvb2t5e3RoZV9yZWZsZWN0aW9uX25ldmVyX2xpZXN9
```

It contains only letters and digits, which looked like Base64. Decoding it:

```python
print(base64.b64decode(data))
```

`zsteg mirror.png` finds the same message on its own, because it tries all the common bit and channel orders automatically.

🚩

```flag
spooky{the_reflection_never_lies}
```
