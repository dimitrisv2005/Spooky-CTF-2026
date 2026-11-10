# Diagraphephobia

I was given a "redacted" PDF, `Diagraphephobia.pdf` — supposedly a Klingon document the Federation intercepted, and I had to recover what was under the redaction.

## Initial Attempts

The first thing I always try on a "redacted" PDF is to just rip the text out, because redaction bars in PDFs are very often just black rectangles *drawn on top* of text that's still fully present in the file.

```bash
pdftotext -layout Diagraphephobia.pdf -
```

Sure enough, the text under the bars came right out. I got a title `Ja'` ("Report" in Klingon) and a big Base64 blob. Decoding the blob gave me 160 bytes — a clean multiple of 16, which screams AES block cipher rather than plain text.

## Finding the key

160 bytes of ciphertext is no good without a key. I went digging in the PDF metadata:

```bash
pdfinfo Diagraphephobia.pdf   # + pikepdf to read the docinfo/XMP
```

The **Subject** field was `lojmIt yIpoSmoH!` — Klingon for *"Open the door!"* — and it's exactly **16 characters**. That's an AES-128 key handed to me on a plate.

For the mode: the PDF also had an embedded image whose raw bytes repeated in clean 16-byte blocks. Repeating blocks on repeating plaintext is the classic fingerprint of **ECB**.

## Solution

```python
import base64
from Crypto.Cipher import AES
ct = base64.b64decode(open("ct.b64").read())
pt = AES.new(b"lojmIt yIpoSmoH!", AES.MODE_ECB).decrypt(ct)
print(pt)
```

Out came readable Klingon followed by the flag:

```
nuqneH
DaHjaj tlhIngan yotlh botlhDaq DIvI' Duj wItu'. Heghlaw' 'ej lonlu'law'...

spooky{qaStaH_nuq}
```

`qaStaH nuq` is Klingon for *"what's happening?"* — a nice touch.

```flag
spooky{qaStaH_nuq}
```
