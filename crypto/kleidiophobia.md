# Kleidiophobia

I was given an HSM "ceremony" dump: `ceremony.log`, `client.py`, `root.pem`,
four intermediate CA certificates `ST-ISS-01..04.pem` with their CSRs, and
`key-inventory.csv`.

The story: a midnight key-generation ceremony produced four intermediate CA
certs, and the logs hid one unusual event. The goal was to recover the
*compromised signing key*, use it to sign a fresh audit message
(ECDSA-P384-SHA384, base64-encoded DER), and submit the signature to the server
to get the flag.

## The anomaly

Three of the four keys follow a boring `GENERATE → CSR` pattern. `OBJ-0003`
does not:

```
KEY  GENERATE  object=OBJ-0003   curve=P-384
HSM  WRAP      object=OBJ-0003   mechanism=AES256-GCM
HSM  UNWRAP    source=OBJ-0003   object=OBJ-0003-R   handler=compat-restore
CSR  CREATE    object=OBJ-0003-R certificate=ST-ISS-03
```

So the key that actually got certified as `ST-ISS-03` is `OBJ-0003-R`, a key
that was wrapped out and restored back through a `compat-restore` handler. That
is clearly the compromised one.

## The rabbit hole (ECDSA attacks that went nowhere)

My first assumption was a classic ECDSA **nonce** flaw, so I parsed every
signature (4 cert signatures, 4 CSR self-signatures, the root self-signature),
confirmed they all verify under SHA-384, and threw the whole arsenal at them:

- **Nonce reuse** — every `r` value is distinct.
- **Small / short nonces** — Hidden Number Problem lattice (validated on
  synthetic data), negative.
- **Shared-MSB nonces**, **consecutive / counter nonces**, and a **bivariate
  small-(d, k)** lattice — all negative.
- **RFC 6979 with a fixed/leaked secret**, **weak seeded PRNG key-gen**,
  **known test-vector keys**, **invalid-curve / small-subgroup** — all negative.

Every signature was cryptographically clean. That was the whole misdirection:
`compat-restore` doesn't produce a weak *nonce*.

## The actual bug — a weak *key*

"Restored in compatibility mode" means the private **scalar** itself was reset
to a trivially small value. A 384-bit key that is really only ~11 bits long
falls instantly to **baby-step / giant-step**:

```python
from fastecdsa.curve import P384
from fastecdsa.point import Point
from cryptography import x509

cert = x509.load_pem_x509_certificate(open("ST-ISS-03.pem", "rb").read())
nm = cert.public_key().public_numbers()
Q = Point(nm.x, nm.y, curve=P384)

G, p = P384.G, P384.p
m = 1 << 20

# baby steps: j*G for j in [1, m)
table, acc = {}, None
for j in range(1, m):
    acc = G if acc is None else acc + G
    table[acc.x] = j

# giant steps: Q - i*(m*G)
mG = m * G
neg_mG = Point(mG.x, (-mG.y) % p, curve=P384)
giant = Q
for i in range(m + 2):
    if giant.x in table:
        d = i * m + table[giant.x]
        if d * G == Q:
            print("private key d =", d)   # -> 1963
            break
    giant = giant + neg_mG
```

`d = 1963`. It reproduces `ST-ISS-03`'s public key exactly (both the cert and
the CSR).

## Signing the challenge

With the key recovered, I pulled a fresh message from the server and signed it:

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
import base64

key = ec.derive_private_key(1963, ec.SECP384R1())
msg = "SPOOKYTRUST-AUDIT-V1:<value from /challenge>".encode()
sig = key.sign(msg, ec.ECDSA(hashes.SHA384()))
print(base64.b64encode(sig).decode())      # submit to /verify
```

The server accepted it and returned the flag. 🚩

```flag
spooky{4T_L345T_1T_15NT_F0UR}
```

The flag — leetspeak for "at least it isn't four" — is a joke about the key
being a small integer. The lesson: a key can look perfectly healthy from the
outside (valid signatures, on-curve point, clean nonces) while the private
scalar itself is trivially small, so BSGS is the right reflex whenever a key
*might* be small but is past plain brute-force range.
