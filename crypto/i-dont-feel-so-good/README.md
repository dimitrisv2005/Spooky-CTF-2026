# I D0n't Feel S0 G00d


I woke up in a mad scientist's lab, queasy, "like you took old medication" — and getting worse. Stinging in my arm, where someone had written `84 53 16 8 28 16 11 6 7`. Two pages were lying around: `chemicals.txt`, a list of 60 lab reagents, and `antidotes.txt`, 61 lines of gibberish. A note on top of both pages said **"Don't forget to move the neon!"**. Flag format `spooky{antidote_here}`.

```
chemicals.txt            antidotes.txt
1   Acetic Acid          1   4xd1n0d3
2   Acetone              2   4xd1n0d3_4mae1b3n
...                      3   4xd1n0d3_x0d_1xmvenon
60  Xylene               ...
                         61  i0e_4b3_x07_meb3n
```

## Breaking the cipher

The gibberish is clearly leetspeak (`4`=a, `3`=e, `1`=i, `0`=o, `5`=s, `7`=t, `6`=g), but stripping the leet alone leaves nonsense, so there's a second layer on the letters.

The note is the key: **neon is element 10**, so the letters are Caesar-shifted by 10. Line 1, `4xd1n0d3`:

| cipher | 4 | x | d | 1 | n | o | d | 3 |
|---|---|---|---|---|---|---|---|---|
| step | leet | −10 | −10 | leet | −10 | leet | −10 | leet |
| plain | a | n | t | i | d | o | t | e |

`antidote`. One quirk worth knowing: the author leeted letters *inconsistently*, so `t` shows up both as `7` (leet) and as `d` (shifted) — `7r3` is `the`. Handle both and everything falls out:

```python
leet = {'4':'a','3':'e','1':'i','0':'o','5':'s','7':'t','6':'g','8':'b','9':'g','2':'z'}

def dec(s):
    out = ''
    for c in s:
        if c in leet:      out += leet[c]                      # leeted digit
        elif c.isalpha():  out += chr((ord(c)-97-10) % 26 + 97) # Caesar -10
        else:              out += c                            # underscore
    return out
```

61 clean English phrases. And every one of them is bait:

```
1   antidote                    9   counter_poison      42  an_apple_a_day
2   antidote_acquired           19  a_day_keeps_the_doctor_away
6   elixir_of_life              35  patient_zero        51  flag_is_not_here
7   the_wrong_elixir            46  no_ciure_available  53  this_is_not_the_flag
...                             55  try_harder          61  you_are_not_cured
```

## The arm

Nine numbers, max 84, and I'm in a chemistry lab — atomic numbers:

```
84  53  16  8   28  16  11  6   7
Po  I   S   O   Ni  S   Na  C   N
```

`PoISONiSNaCN` → **"POISON IS NaCN"**. Sodium cyanide. The `Po`/`Ni`/`Na` symbols deliberately straddle word boundaries, which is a nice touch.

## Where I wasted an hour

I assumed the 61 phrases were 60 decoys plus one semantically correct "antidote", and started guessing the ones that sounded like a cure. `counter_poison`, `elixir_of_life`, `antidote_acquired`, `an_apple_a_day`, `patient_zero`, `trust_the_process`, `what_doesnt_kill_you`, `poison_is_bad_for_you`. All rejected. The decoy set is built specifically to beat this: every tempting line has a twin that mocks it (`antidote` is killed by `antidote_not_included` and `the_antidote_is_a_lie`, `elixir_of_life` by `the_wrong_elixir`, the apple line by `ask_your_doctor_not_me`).

Things I checked and ruled out along the way, so you don't repeat them:

- **A line encoded with a different shift**, which would mark the flag. I brute-forced all 26 shifts against a dictionary for all 61 lines — shift 10 is optimal for every single line. No outlier.
- **The nine numbers as indices** into basically anything: characters, letters-only, word initials, line initials, raw ciphertext, both files, forward, reversed, 0- and 1-based, ±10 offsets. Noise in every variant.
- **An encoding fingerprint** — counting leeted vs. shifted characters per line, hoping one line was encoded "purely". No pattern.
- **Element-symbol spellings of the phrases.** Only four of the 61 are fully spellable (`lab_rat_lives` = La-B-Ra-Tl-I-V-Es, `the_spooky_reaction` = Th-Es-P-O-O-K-Y-Re-Ac-Ti-O-N, `poison_is_not_bag`, `poison_is_bag_for_no_one` = P-O-I-S-O-N-I-S-B-Ag-F-O-Rn-O-O-**Ne**). That last one uses neon, which felt like the note paying off. It isn't the flag.
- **Element-symbol spellings of the chemicals.** Exactly one works: `Barium Carbonate` = B-Ar-I-U-Mc-Ar-B-O-Na-Te. The author saw that coming — line 60 of the antidotes is literally `barium_is_not_here`.
- **A real-world cyanide antidote from the reagent list.** The actual antidotes are oxygen, sodium thiosulfate, amyl/sodium nitrite, 4-DMAP, hydroxocobalamin and dicobalt edetate. None of them is on the page — the closest is Cobalt Chloride, cobalt being the cyanide binder in hydroxocobalamin. Also not the flag.

## The solution

The chemicals list isn't flavour and it isn't a menu of antidotes — **it's an index**. `NaCN` is **Sodium Cyanide, line 52**. Take line 52 of the antidotes file:

```
z0150x_15_l46_p0b_i0e

z0150x -> p o i s o n
15     -> i s
l46    -> b a g
p0b    -> f o r
i0e    -> y o u
```

What confirms it is the neighbourhood. The author fenced the answer in with off-by-one bait on both sides:

```
50  wrong_button_buddy       <- off-by-two
51  flag_is_not_here         <- off-by-one low
52  poison_is_bag_for_you    <- Sodium Cyanide = chemicals line 52
53  this_is_not_the_flag     <- off-by-one high
54  nice_try_buddy           <- off-by-two
```

Two deliberate design details I'd read backwards for ages:

- **`bag` is not a typo.** It's what stops the flag being guessable in English — you can only get `bag` by actually decoding. Line 59, `poison_is_bad_for_you`, is the trap for anyone who "fixes" it, and lines 56–58 (`poison_is_not_bag`, `bag_is_not_poison`, `poison_is_bag_for_no_one`) are scrambles of the same sentence planted for the same reason.
- **"Move the neon" is only the shift hint.** I kept trying to spend it twice — inserting Neon into the alphabetical chemicals list (it lands at position 35, which conveniently makes the list 61 long, matching the antidotes file), or shifting the index by 10 (52−10 = 42 = `an_apple_a_day`). Both are rabbit holes, and `this_is_not_the_flag` sitting at 53 is exactly the punishment for the neon-insertion version.

🚩

```flag
spooky{poison_is_bag_for_you}
```
