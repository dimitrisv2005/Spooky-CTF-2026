# I Feel Like Someone's Watching Me

**Category:** Crypto

## The challenge

> A letter is found beside a tombstone in a graveyard, but it seems to have been scrambled around.

The attachment was a full letter, something like `Ypejpof Erpveaypj,` at the top, that read like normal English with every letter swapped out.

## Figuring it out

The punctuation, apostrophes and word lengths were all intact, only the letters were replaced. That's a monoalphabetic substitution cipher: a fixed random mapping from each letter to another. ROT13 is the baby version of this with a fixed shift, but here the alphabet is scrambled, so I needed a solver that works off English letter patterns.

A couple of manual anchors to sanity-check it: `D` on its own is almost certainly `I`, and the word `fcp` showing up everywhere is almost certainly `the`.

## Solving it

I pasted the whole letter into [quipqiup](https://quipqiup.com) and hit Solve. It figures out the mapping from word patterns and gave back the plaintext letter. The second-to-last paragraph spelled out the flag and how to format it.

One gotcha: the flag has `eyez` with a `z`. That isn't a solver mistake. In the body of the letter, `s` encrypts to `o` (for example `Odagpjprz` = `Sincerely`), but in the flag clue the author used a different letter on purpose, so the `z` is real.

## Flag

```
spooky{eyez_are_watching_me}
```

## Takeaway

Readable sentence structure with swapped letters means substitution, and quipqiup cracks those in one click. Double-check any letter that looks off, because the author can plant a deliberate one in the flag.
