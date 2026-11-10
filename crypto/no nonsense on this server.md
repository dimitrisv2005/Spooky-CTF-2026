# No Nonsense On This Server

I was handed a set of participant files for a proprietary remote-access protocol called **SP00KY**, running on a recovered server at `18.222.247.20:19160`. The brief: the box still has its original users and filesystem, but the admin credentials are lost. I get a general-purpose account — a private key `general.pem` for the user `general` — and I have to read `/home/admin/flag.txt`. The files include a reference C client I can build with `make`, plus the protocol source under `common/` and `docs/PROTOCOL.md`.

## Getting a client going
First I built the reference client so I had something that spoke the protocol. The docs say `make client`, but the actual Makefile target is `spooky-client`:

```
make spooky-client
./spooky-client --host 18.222.247.20 --port 19160 --user general --key general.pem
```

The handshake is simple: `HELLO` → banner, `AUTH_START` with the username → the server sends a 32-byte challenge, I sign it with my ECDSA key and send `AUTH_PROVE`, then I get a shell that runs commands via `EXEC`. The message I sign is:

```
"SP00KY-AUTH-v1" || len(username) || username || challenge
```

signed with ECDSA over NIST P-256 / SHA-256. Each user has one registered public key the server checks against. I eventually reimplemented the whole client in pure Python so I could script the crypto, but the C client is enough to look around.

## Looking around as general
Once authenticated as `general`, I poked at the filesystem:

```
whoami        -> general
ls /home      -> admin  general
cat /home/admin/flag.txt   -> permission denied
```

No surprise — I can't read admin's flag as general. So I went looking for anything that leaks admin's key material, and the obvious place was the logs:

```
cat /var/log/auth.log
```

That dumped ~110 KB of audit records. Each line looks like this:

```
timestamp_ms=1705029267000 username=admin event_hex=6163...3134 public_key=040bd5...f816 r=ca7b85...ce49 s=778a3b...774e
```

## The audit log is signed
`PROTOCOL.md` has a section on "authentication log records": every audit line is **ECDSA-signed**, as `(r, s)`, over a canonical `SP00KY-LOG-v1` record — and crucially it's signed with the **same per-user key** used to log in. The record layout is:

```
"SP00KY-LOG-v1" || u64_be(timestamp_ms) || u8(len(user)) || user || u16_be(len(event)) || event
```

So `event_hex` is just the event bytes (e.g. `accepted signature for admin from 10.7.0.14`), and each line even carries the signer's `public_key`. That means I can rebuild the exact message that was signed for any line.

## The vulnerability — reused k
ECDSA has one famous way to die: **reuse the nonce `k`**. If the same `k` signs two different messages, both signatures share the same `r`, and the private key falls straight out. So I grouped every signature by its `r` value and looked for a collision.

Two of admin's lines had an identical `r`:

```
event: "accepted signature for admin from 10.7.0.14"   r=ca7b85...ce49  s=778a3b...774e
event: "session opened for admin from 10.7.0.14"       r=ca7b85...ce49  s=7ee53f...0227
```

Same `r`, different messages → same `k`. Game over. With `z1, z2` the SHA-256 hashes (as integers) of the two reconstructed records, and `n` the curve order:

```
k = (z1 - z2) * inv(s1 - s2) mod n
d = (s1 * k - z1) * inv(r) mod n
```

`d` is admin's private key. I derived the public key from my candidate `d` and confirmed it matched the `public_key=` field on admin's log lines (ECDSA sign ambiguity means you test a couple of ± variants and keep the one whose `d*G` matches).

## Logging in as admin
Recovered scalar:

```
d = 0xb4ade2a2e9404047f56f64d4e10bed17932bb5863180881f7506e90a9c3ebbb1
```

From here it's just a normal login, except I sign the `SP00KY-AUTH-v1` challenge with the recovered admin key instead of my own. The server can't tell the difference — it's the right key:

```python
# core of the attack, pure-python P-256
k = (z1 - z2) * inv(s1 - s2, n) % n
d = (s1 * k - z1) * inv(r, n) % n          # admin private scalar
assert pt_mul(d, G) == admin_pubkey        # matches the key in the log

# then: login as "admin", sign the challenge with d, and:
run_cmd(sock, "cat /home/admin/flag.txt")
```

Logged in as `admin`, `whoami` confirmed it, and I read the flag. The flag name is the punchline:

```flag
spooky{reused_k_no_nons3nse_89f3ae32316e}
```
🚩
