# Frankenstein's Password Generator

 *Binrev — 75 points*

> Dr. Frankenstein left behind a strange password generator in an abandoned NJIT laboratory. The machine refuses to start without an activation phrase. His last notebook entry reads, "A bolt at midnight gave it life." Can you figure out what the program expects and wake the creature?

I was given a single x86-64 ELF, `frankenstein`. No server — fully local static reversing.

## Taking it apart

```bash
file ./frankenstein
nm ./frankenstein | grep -i ' t \| T '
objdump -d -M intel ./frankenstein
```

Two routines matter: a **phrase check**, and a **flag decode** that only runs once the phrase matches. The constants they use live in `.rodata` (vaddr `0x402000`, file offset `0x2000`):

- 14 "expected" bytes at `0x402010` — the phrase-check target
- 29 bytes of flag ciphertext at `0x402020`

## Stage 1 — recover the activation phrase

The check demands exactly **14 characters**, and for each position `i`:

```
((input[i] ^ 0x5d) + 7*i + 0x0b) & 0xff == expected[i]
```

Invert it and the phrase falls straight out:

```python
data = open("frankenstein","rb").read()
at = lambda v,n: data[v-0x402000+0x2000 : v-0x402000+0x2000+n]
expected = at(0x402010, 14)
phrase = bytes(((expected[i] - 7*i - 0x0b) & 0xff) ^ 0x5d for i in range(14))
print(phrase.decode())   # BOLTATMIDNIGHT
```

→ **`BOLTATMIDNIGHT`**, exactly "A **bolt** at **midnight**." The notebook entry was the hint all along.

## Stage 2 — decode the flag

Once the phrase matches, a second routine XOR-decodes the 29-byte blob using the phrase itself as a rolling key:

```
flag[i] = cipher[i] ^ phrase[i % 14] ^ ((13*i + 0x39) & 0xff)
```

The one thing that tripped me up was the key index. It's `i % 14` (the full phrase), **not** `i % 7`. In the disassembly the modulo computes `7q` via `sub rax,rdx`, then an `add rax,rax` doubles it to `14q` — so the remainder is taken mod 14. With mod 7 the prefix and suffix decode fine but the middle garbles, which is exactly what sent me back to re-read the division.

```python
cipher = at(0x402020, 29)
flag = bytes(((cipher[i] ^ phrase[i % 14]) ^ ((13*i + 0x39) & 0xff)) & 0xff for i in range(29))
print(flag.decode())
```

Confirmed by running the real binary:

```bash
printf 'BOLTATMIDNIGHT\n' | ./frankenstein
```

It's alive. 🧟

🚩

```flag
spooky{its_alive_at_midnight}
```
