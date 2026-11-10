# Too Much Love is Scary

 *Binrev — 50 points*

> Last time I loved I was left broken and in shambles. That's when I realized that my heart could only hold so much, I must protect it. So I won't fall in love again, it's just too scary…

Behind the romantic framing is an x86-64 ELF that wants some input, validates it, and then reveals a hidden flag.

## What it does

```bash
objdump -d -M intel ./philophobia
```

The logic:

1. Prompts for **two numbers** — a `start` and an `end` position.
2. Prompts for a **line of text**.
3. Checks that a **20-character substring** of the input, taken at the given position, matches the opening of **Shakespeare's Sonnet 18**: *"Shall I compare thee to a summer's day?"*
4. Calls `print_flag(start, end)`, which uses `(end - start + 0x47)` as a single-byte **XOR key** to decode a hidden flag string.

## Solving

I don't have to guess the numbers blind — I can recover the key by brute force, since only one of the 256 single-byte XOR keys yields printable ASCII:

```python
enc = bytes([...])   # encoded flag bytes pulled from the binary
for k in range(256):
    out = bytes(b ^ k for b in enc)
    if all(32 <= c < 127 for c in out) and b'{' in out:
        print(k, k-0x47, out)
```

Exactly one readable candidate, with key **`0x5A`**. Through the `(end - start) + 0x47` relation, `0x5A` means `end - start = 19` — a 20-character span. So a valid input is:

```
0 19
Shall I compare thee to a summer's day?
```

`start = 0`, `end = 19` → difference 19 → XOR key `0x5A`, and the Shakespeare line satisfies the 20-char substring check. Any pair with `end - start = 19` works, as long as the sonnet line begins at position `start`.

Verify against the real binary:

```bash
printf '0 19\nShall I compare thee to a summer'\''s day?\n' | ./philophobia
```

It prints the decoded flag.

🚩

```flag
spooky{m4yb3_1_n33d_t0_10v3_mys31f}
```
