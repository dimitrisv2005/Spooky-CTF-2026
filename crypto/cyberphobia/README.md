# Cyberphobia

I was given two files: `data.txt` and `backup.py`.

`data.txt` handed me three hex blobs and told me to read the backup script:

```
Known message:     546865206861756e746564207661756c7420636c6f736573206174206d69646e696768742e2053746179206f7574736964652e20202020202020202020202020
Encrypted message: e4a8bb39921d6f0e3940a040ae22a1afc698fdeb3058ea8e1002fe25142227c6f7f018ddf3eb9ce75e69dbdc59720fcffd98a9c0bb9f03f0d644f34c68a4c306
Encrypted flag:    c3b0b176910561033e16f151920887be9298bea77f0bafdd1043aa25596b6388beb75089fdebefb31f30db930c265c86b9dda7c0bb9f03f0d644f34c68a4c306
```

`backup.py`:

```python
from Crypto.Cipher import AES

def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CTR, nonce=b"ghost123", initial_value=0)
    return cipher.encrypt(message.ljust(64, b" "))
```

## Spotting the bug

AES in CTR mode isn't really a block cipher anymore — it generates a
**keystream** from `(key, nonce, counter)` and XORs it with the plaintext,
exactly like a one-time pad. The catch is that a one-time pad is only safe if
the keystream is used *once*.

Here the key never changes, the nonce is hardcoded to `b"ghost123"`, and the
counter always starts at `initial_value=0`. So **every** message gets XOR'd
with the identical keystream. Classic keystream reuse.

A nice tell confirms it: the last ~20 bytes of the "encrypted message" and the
"encrypted flag" are byte-for-byte identical. That's because both plaintexts
are space-padded with `.ljust(64, b" ")`, and the same plaintext under the same
keystream produces the same ciphertext.

## Recovering the flag

Since the keystream is constant:

```
keystream = known_message XOR encrypted_message
flag      = encrypted_flag XOR keystream
```

```python
known    = bytes.fromhex("546865206861756e746564207661756c7420636c6f736573206174206d69646e696768742e2053746179206f7574736964652e20202020202020202020202020")
enc_msg  = bytes.fromhex("e4a8bb39921d6f0e3940a040ae22a1afc698fdeb3058ea8e1002fe25142227c6f7f018ddf3eb9ce75e69dbdc59720fcffd98a9c0bb9f03f0d644f34c68a4c306")
enc_flag = bytes.fromhex("c3b0b176910561033e16f151920887be9298bea77f0bafdd1043aa25596b6388beb75089fdebefb31f30db930c265c86b9dda7c0bb9f03f0d644f34c68a4c306")

keystream = bytes(a ^ b for a, b in zip(known, enc_msg))
flag      = bytes(a ^ b for a, b in zip(enc_flag, keystream))
print(flag.decode().rstrip())
```

(The known plaintext even decodes to a nice bit of flavor: *"The haunted vault
closes at midnight. Stay outside."*) 🚩

```flag
spooky{cs351JKS}
```

**Fix:** use a fresh random nonce per message (and store it alongside the
ciphertext), or better yet an authenticated mode like AES-GCM.
