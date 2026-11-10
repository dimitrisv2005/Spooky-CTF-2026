# The Haunted Portrait

**Category:** Forensics

## The challenge

> An old portrait was recently discovered in a storage room at NJIT just before Halloween. Students claim the painting changes when viewed at night, and some believe a secret message is hidden inside it. The university's security team examined the image but couldn't find anything unusual. Can you uncover what the portrait has been hiding all these years?

A single PNG of a creepy old portrait.

## Figuring it out

I ran the usual quick checks first: `strings` for a plaintext flag, the metadata, and the end of the file for anything appended. All clean. "Security team couldn't find anything unusual" was basically telling me it's not in the obvious places.

The phrase I kept coming back to was "changes when viewed at night." That points at the pixels themselves rather than the file structure, which means steganography in the low bits of the image.

## Solving it

I loaded the PNG into a bit-plane viewer (I used [StegOnline](https://georgeom.net/StegOnline), the Python route with Pillow works too) and stepped through the planes. The **blue channel, bit 0** plane wasn't noise, it had text drawn into it, including the line `THE DEAD SPEAK IN ROT13` and a ciphertext that looked like a flag with the letters shifted (`fcbbxl{...}`, same shape as `spooky{...}`).

From there it was just ROT13 in CyberChef on the revealed ciphertext.

## Flag

```
spooky{portraits_keep_secrets}
```

## Takeaway

If strings and metadata come up empty and the prompt hints at something visual ("at night", "look closer"), go to the bit planes. And a stego layer will often hand you a second step rather than the flag directly, here the plane told me to run ROT13.
