# Xenoglossophobia

I was given a 2.2 MB `serial-capture.log`. The flavor text leaned hard on *"so many languages... so many ways to interpret data... I feel like I'm cutting onions"* — onions meaning **layers**.

## Peeling layer 1 — the serial protocol

The capture is a two-way serial link: `>` for one direction, `<` for the other. The `>` side sends fixed 132-byte packets that start `01 <block> <~block>` with an incrementing block number and its complement, and the `<` side only ever replies `15` (NAK) once then `06` (ACK) repeatedly. That's textbook **XMODEM** (`SOH` + block + ~block + 128 data bytes + checksum = 132).

I parsed the hex column out of the log, concatenated the `>` stream, and de-framed it — stripping the 3-byte header and 1-byte checksum from each packet to recover the 128 data bytes. Every checksum validated, so the framing was clean.

## Peeling layer 2 — two files, not one

While de-framing I noticed an `EOT` (`04`) partway through, followed by a **second** XMODEM session that restarted at block `01`. So there were two transfers:

- **Transfer 0** reassembled to a JPEG — a *Supermarket Simulator* screenshot (`ff d8 ff e0 ... JFIF`), padded out with XMODEM's `0x1a`.
- **Transfer 1** was a short text file, and *this* is where "so many languages" kicks in — it's written in **Latin and Portuguese**:

> *"Ut clavem invenias ad plura de 'loco' cognoscenda, intellegere debes quid imago tibi significet. Est id quod 'supermercado' vocant!"*
>
> → "To find the **key**, you must understand what the image means to you. It's what they call a **supermercado** (supermarket)!"

## Peeling layer 3 — steghide

That's a passphrase hint pointing straight at the JPEG. The image had no appended data, no weird markers, nothing in `strings` — so JPEG-domain stego. `steghide` with the passphrase from the clue did it:

```bash
steghide extract -sf carved.jpg -p "supermercado" -xf out.txt
```

## Peeling layer 4 — mixed encodings

The extracted message is another Portuguese note, and the flag inside it is deliberately written in **two different encodings at once** (the "so many ways to interpret data" part): the first half as `\xHH` hex escapes, the second half as space-separated decimal char codes.

```
...\x73\x70\x6f\x6f\x6b\x79\x7b\x6d\x75\x31\x74\x69\x70\x6c\x33\x5f 108 64 110 103 117 64 103 101 115 125
     s  p  o  o  k  y  {  m  u  1  t  i  p  l  3  _    l  @   n   g   u  @   g   e   s   }
```

Decode both halves and join (the gap between them is just the seam between the two encodings — the `_` is the real separator):

```flag
spooky{mu1tipl3_l@ngu@ges}
```
