# Elves can be Spooky Too

 *Binrev — 377 points*

> The elves left you a very small doorway.

I'm given a host, a port (`nc 3.129.162.36 31903`) and a byte budget. I have to send an x86-64 Linux ELF that:

1. is **at most 112 bytes** (the service prints the live limit on connect),
2. writes its **own exact bytes** to stdout (a *quine*),
3. exits with status **0**.

Protocol: connect, read the banner, send `SIZE <n>\n`, then exactly `<n>` raw bytes. The reply is `PASS`/`FLAG` or `FAIL`. No exploitation here — pure ELF golf.

## The quine idea

A `PT_LOAD` program header maps the whole file (offset `0` → `p_filesz`) into memory at the load address `0x400000`. So the ELF header bytes are themselves sitting in memory at `0x400000`, and the program only has to:

```asm
write(1, 0x400000, 112)   ; dump the entire mapped file = itself
exit(0)
```

What it writes is a byte-for-byte image of the file → stdout equals the file.

## The 112-byte problem

A normal ELF64 header is **64 bytes** and one program header is **56 bytes** → 120, already over budget. The tricks that get me to exactly 112:

- **Overlap** the program header into the tail of the ELF header by setting `e_phoff = 56`. That's the lowest offset that still keeps `e_phentsize` (which the kernel validates must be 56) intact. This pins the file at exactly **112 bytes** — almost certainly why the limit is set there.
- The overlap is engineered so shared bytes satisfy both structures at once, e.g. `p_type = PT_LOAD (1)` doubles as `e_phnum = 1`.
- The ~22 bytes of machine code live in header fields the kernel ignores during `execve`: the `e_ident` padding (entry point `0x400008`), `e_shoff`/`e_flags`, and `p_paddr` — stitched together with two short relative jumps.

## Building it

```python
import struct
F = 112
b = bytearray(F)
def put(off, data): b[off:off+len(data)] = data

# ---- ELF64 header ----
put(0, b'\x7fELF'); b[4]=2; b[5]=1; b[6]=1
put(16, struct.pack('<H',2))        # e_type = ET_EXEC
put(18, struct.pack('<H',0x3e))     # e_machine = x86-64
put(20, struct.pack('<I',1))        # e_version
put(24, struct.pack('<Q',0x400008)) # e_entry -> code region A
put(32, struct.pack('<Q',56))       # e_phoff = 56 (phdr overlaps ehdr tail)
put(54, struct.pack('<H',56))       # e_phentsize = 56 (must stay intact)
# ---- program header at offset 56 ----
put(56, struct.pack('<I',1))        # p_type = PT_LOAD (low word => e_phnum=1)
put(60, struct.pack('<I',5))        # p_flags = R+X
put(64, struct.pack('<Q',0))        # p_offset = 0
put(72, struct.pack('<Q',0x400000)) # p_vaddr
put(88, struct.pack('<Q',F))        # p_filesz = 112
put(96, struct.pack('<Q',F))        # p_memsz  = 112
put(104,struct.pack('<Q',0x1000))   # p_align
# ---- code (hidden in unused header fields, chained with short jmps) ----
put(8,  bytes([0x6a,0x01,0x5f,0x89,0xf8,0xeb,0x19]))                      # A: rdi=1; eax=1; jmp B
put(40, bytes([0xbe,0x00,0x00,0x40,0x00,0x6a,0x70,0x5a,0x0f,0x05,0xeb,0x1c])) # B: rsi=0x400000; rdx=112; write; jmp C
put(80, bytes([0x31,0xff,0x6a,0x3c,0x58,0x0f,0x05]))                      # C: rdi=0; rax=60; exit

open("quine","wb").write(b)
```

Verify it reproduces itself:

```bash
chmod +x quine
./quine > out.bin
echo "exit: $?"
cmp quine out.bin && echo "QUINE OK"   # stdout == own 112 bytes
```

Full hex of the ELF:

```
7f 45 4c 46 02 01 01 00 6a 01 5f 89 f8 eb 19 00
02 00 3e 00 01 00 00 00 08 00 40 00 00 00 00 00
38 00 00 00 00 00 00 00 be 00 00 40 00 6a 70 5a
0f 05 eb 1c 00 00 38 00 01 00 00 00 05 00 00 00
00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00
31 ff 6a 3c 58 0f 05 00 70 00 00 00 00 00 00 00
70 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00
```

## Submitting

```python
#!/usr/bin/env python3
import socket, time
HOST, PORT = "3.129.162.36", 31903
elf = open("quine","rb").read(); assert len(elf) == 112

s = socket.socket(); s.settimeout(10); s.connect((HOST, PORT))
time.sleep(0.3); print(s.recv(8192).decode(errors="replace"))   # banner
s.sendall(b"SIZE %d\n" % len(elf)); time.sleep(0.2); s.sendall(elf)

out = b""
s.settimeout(6)
try:
    while True:
        c = s.recv(8192)
        if not c: break
        out += c
except socket.timeout:
    pass
print(out.decode(errors="replace"))   # PASS / FLAG / FAIL
```

```bash
python3 submit.py
```

Manual `nc` alternative (racey, prefer the script):

```bash
{ printf 'SIZE 112\n'; cat quine; } | nc 3.129.162.36 31903
```

The service verifies the quine and hands back the flag.

🚩

```flag
spooky{phdr_in_ehdr_c2d021cc4fc5}
```
