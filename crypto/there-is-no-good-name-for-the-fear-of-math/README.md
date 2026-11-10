# There is no good name for the fear of math.

 *Crypto — 474 points*

I was given the participant files for a custom "Diffie-Hellman"-style key exchange, plus the ciphertext of the flag. The twist — and the "fear of math" — is that the whole thing is built on a **non-associative** operation, so the usual group-theory intuition goes out the window.

## The scheme

Elements are **tuples of four coordinates** `(α, β, γ, δ)` combined with modular arithmetic over two primes `p` and `q`, plus:

- an **associator** function (measuring how far the operation strays from associative),
- a **masking** function based on **SHAKE-256**, which turns the shared key into a keystream for the ciphertext.

## Two flaws that break it completely

**1. The public key leaks the private structure.** The first coordinate is **invariant under conjugation**, so the public key's `β` and `γ` become **linearly solvable** from the private key's structure for any guessed value of `α`.

**2. The shared secret doesn't depend on the parts I don't know.** The shared-key computation:

- never depends on the `δ` coordinate, and
- the `α`-dependence **cancels out entirely**.

So *any* guessed `α` — 0, 1, 12345, anything — produces the **identical** shared key `K`.

## Solving

```
1. Pick any α (e.g. α = 0).
2. Linearly solve for β, γ from the public key.
3. Compute the shared key K — independent of δ and of the α choice.
4. keystream = SHAKE-256(K); XOR it against the ciphertext.
```

Sanity checks I ran:

- multiple `α` values (0, 1, 12345) all give the **same** `K`;
- `μ` has order exactly `p mod q`.

XORing the recovered keystream against the ciphertext drops out the flag — and its wording maps directly onto the mathematical flaw that broke the scheme. The recovered plaintext was `spooky_scary_nonassociative_diffie_hellman`; submitted in the challenge's `spooky{...}` wrapping.

🚩

```flag
spooky{scary_nonassociative_diffie_hellman}
```
