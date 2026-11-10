#!/usr/bin/env python3
# Submit the 112-byte self-printing ELF to the SpookyCTF doorway service.
import socket, re, sys, time

HOST, PORT = "3.129.162.36", 31903
elf = open("quine", "rb").read()
assert len(elf) == 112, len(elf)

s = socket.socket(); s.settimeout(10)
s.connect((HOST, PORT))

# 1) read the banner (it prints the live byte limit)
time.sleep(0.3)
banner = s.recv(8192)
sys.stdout.write(banner.decode(errors="replace")); sys.stdout.flush()

# sanity: if the banner states a limit, make sure we're within it
m = re.search(rb"(\d{2,4})", banner)
if m:
    limit = int(m.group(1))
    if len(elf) > limit:
        print(f"\n[!] our ELF is {len(elf)}B but limit is {limit}B", file=sys.stderr)

# 2) announce the size, then 3) send exactly that many raw bytes
s.sendall(b"SIZE %d\n" % len(elf))
time.sleep(0.2)
s.sendall(elf)

# 4) read the verdict (PASS / FLAG / FAIL)
s.settimeout(6)
out = b""
try:
    while True:
        chunk = s.recv(8192)
        if not chunk: break
        out += chunk
except socket.timeout:
    pass
s.close()
print("\n----- server reply -----")
print(out.decode(errors="replace"))
