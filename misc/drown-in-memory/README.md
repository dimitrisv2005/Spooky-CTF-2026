# Drown in Memory

 *Misc / Reverse Engineering (hard) — 924 points*

> 180 meters below the surface, your cage opens into darkness. Follow the flickering wreck lights, scavenge oxygen, and reach the submarine before it finds you.

What I got was a downloaded **Windows game package** — no obvious "challenge" to it at first. It turned out to be a reverse-engineering challenge: the game is winnable only by cheating, and winning is what prints the flag. The title, *Drown in Memory*, is the hint — the intended cheat is editing the game's **memory**.

## What's in the package

```bash
unzip -l Drown-in-Memory_Windows.zip
```

A packaged **Unreal Engine 5** shipping build, internally named **"Abyss"**:

- `Abyss.exe` — launcher; the real binary is `Abyss/Binaries/Win64/Abyss-Win64-Shipping.exe`
- `Abyss/Content/Paks/` — levels/models/audio in Unreal's IoStore format (`.pak`, `.ucas`, `.utoc`)

## Getting at the assets and code

The paks are IoStore containers. `retoc` (github.com/trumank/retoc) is the usual unpacker, but it needs an Oodle decompression lib it couldn't auto-download in my sandbox, and its asset-name resolution didn't support this engine version. The workaround:

- `retoc unpack-raw` for raw chunk extraction, plus the `pyooz` Python package (`pip install --break-system-packages pyooz`) and a small custom IoStore parser for the containers.
- For the executable, `pefile` + `capstone` (x86-64) to disassemble, with a RIP-relative reference resolver to tie string literals and data constants back to the code that uses them.

Pulling strings out of the config pak gave the backend:

```
https://d2xe63kuz25gcn.cloudfront.net
```

So the game is a thin client — it streams inputs to a server every 0.1 s and the server runs all the real logic.

## The actual vulnerability

Disassembling the client/server protocol showed what the server trusts. Almost everything — oxygen, stamina, health, position — is **server-authoritative**: the client just displays whatever the server sends back. Editing those in memory changes only the HUD; the next server update overwrites them. That's a dead end (and why an "unlimited health/stamina" cheat can't work here).

The **one** value the client reports and the server trusts is the **suit capacity**. And that's exactly the wall the game puts in front of you: the stock suit (capacity `1.0`) can't survive the final ~190 m swim from the last oxygen tank to the submarine — the game literally says *"FINAL GAP EXCEEDS STOCK SUIT RANGE."* The server accepts capacities from about `0.5` up to `3.0`, **if** they come with a correct guard value.

The client keeps a calibration struct on the heap:

```
+0x08  float   capacity   (stock 1.0; server accepts 0.5 .. 3.0)
+0x0C  uint32  guard      = float_bits(capacity) ^ cookie ^ 0xA731CF29
+0x10  uint32  cookie     (sent by the server in /v1/session)
```

The final stretch needs `capacity > 1.01`. So the cheat is: raise `capacity` in memory to `3.0` **and** recompute `guard` so the server can't tell it was tampered with.

## The exploit — `suit_patch.py`

A pure-Python Windows memory patcher (no extra packages). It scans the running game's process memory for the `capacity / guard / cookie` triple, then overwrites `capacity = 3.0` and writes a matching `guard = float_bits(3.0) ^ cookie ^ 0xA731CF29`. It re-applies after each restart/reset.

```python
# core of the patch:
#   find the struct, then:
#   write float 3.0 at +0x08
#   write (struct.unpack('<I', struct.pack('<f', 3.0))[0] ^ cookie ^ 0xA731CF29) at +0x0C
```

Delivered straight into the game folder and run alongside the game:

```
cd C:\Users\<you>\Downloads\Drown-in-Memory_Windows
python suit_patch.py        # wait for the [+] ... capacity=3.0 line
```

## Beating it to get the flag

The patch doesn't print the flag — it makes the game winnable. With 3× range:

1. Collect the 6 yellow oxygen tanks in order (the HUD points to the nearest).
2. If the shark notices you, hide in the green **COVER** shelter behind a wreck, kill the light (F) and hold E until **PATROL CLEAR**.
3. After 6/6, follow the **SUBMARINE** marker to the airlock.
4. On escape, the server sends the **flag**, which the game renders as lit-up blocks — read it left-to-right, top-to-bottom.

🚩

```flag
spooky{!NjEc70R-P0wer-u5eR}
```
