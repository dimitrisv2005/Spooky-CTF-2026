# Stash the Hash

 *Forensics — 75 points*

The challenge ships a little bundle: a `UserAccountInfo.txt`, a password-protected archive `secretKnowledgeFolder.7z`, and (once you're through) an image `secretKnowledge.png`. It's a chain — crack a hash, open the archive, then dig the flag out of the image.

## Step 1 — the account dump

`UserAccountInfo.txt` is a leaked account record:

```
Username: dleeds
Password: ad7bcd7ab3cc113f496e1840bc582bbd
Full Name: Daniel Leeds
Display Name: DevilLeeds
Email: dleeds@galloway.com
Department: Horror Management
Employee ID: NJ-062805
...
```

That "Password" field is 32 hex characters — a classic **MD5 hash**, not a plaintext password. (The Jersey-Devil flavour is all over this: *Leeds*, *DevilLeeds*, the `NJ-` employee ID — the Leeds Devil legend.)

## Step 2 — crack the hash

MD5 is unsalted and fast, so throw it at a wordlist:

```bash
echo 'ad7bcd7ab3cc113f496e1840bc582bbd' > hash.txt
hashcat -m 0 -a 0 hash.txt rockyou.txt
# or:
john --format=raw-md5 --wordlist=rockyou.txt hash.txt
```

The recovered plaintext is the **password for the 7z archive**.

## Step 3 — open the archive

```bash
7z x secretKnowledgeFolder.7z            # enter the cracked password
```

Inside is **`secretKnowledge.png`** (700×700, RGBA).

## Step 4 — the image is hiding the flag (LSB stego)

The usual checks come back empty:

```bash
exiftool secretKnowledge.png      # metadata / EXIF  -> nothing
binwalk secretKnowledge.png       # trailing / appended data -> nothing
```

But the PNG is **RGBA with no auxiliary chunks** — a spurious alpha channel on an otherwise bare image is a classic tell for **LSB (least-significant-bit) steganography**. Pull the LSB of each channel and render it; the **red channel's LSB plane** shows readable text in the top-left corner:

```python
from PIL import Image
import numpy as np

a = np.array(Image.open("secretKnowledge.png"))
lsb_red = (a[:, :, 0] & 1) * 255          # isolate red LSB, scale to 0/255
Image.fromarray(lsb_red.astype("uint8")).save("red_lsb.png")
```

Opening `red_lsb.png` shows the flag — and it ties back to the account dump (`dleeds` / *DevilLeeds*).

Faster next time: `zsteg secretKnowledge.png` or StegSolve's bit-plane browser auto-scan all planes instead of doing it by hand.

🚩

```flag
spooky{dleeds_isa_devil}
```
