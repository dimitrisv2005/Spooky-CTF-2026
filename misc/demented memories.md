# Demented Memories

Challenge by *<author>*

I was provided with a 7z archive called `forgotten-playground.7z`, with the challenge text saying that my memories are leaving me, that I miss the days of the past, and that I need to recover the fragmented parts of the past.

## Initial Attempts

My machine didn't have `7z` installed, so I listed and extracted the archive with Python's `py7zr` instead. It wasn't password protected and contained a folder with:

- a `README.md` (*"a workshop of beloved memories and fragmented pasts"*)
- an image called `the_golden_age.jpg`
- 71 files named `fog1.fog` to `fog71.fog`, six of them hidden (`.fog11.fog`, `.fog21.fog`, ... `.fog61.fog`)
- one bigger `fog.fog` with 80 lines
- a `.git` folder

Every `.fog` file was just a 32-character hex string, so my first thought was that they were MD5 hashes of single characters that would spell out the flag. I built a lookup table of the MD5 of every printable 1–3 character string and every number from 0 to 99999 and checked all 151 hashes against it. Nothing matched.

I also looked at `the_golden_age.jpg`. It's a "the 2010s" nostalgia collage. `file` reported a normal 1280x720 JPEG, `strings` only turned up noise, and the file ended right at the JPEG end marker (`FF D9`), so nothing was appended after the image.

## Digging Through Git

Since the folder was a git repo, I checked `.git/config` first to make sure there was nothing sketchy in it (like an `fsmonitor` or hooks path that would run code). It was a normal config pointing to a GitHub remote, so I went ahead with git.

```bash
git log --all --stat
```

The history told a story:

```
0f00424  MEMORY WIPE INITIALIZATION   (invisible_influence)  -> retrospective.c | 55 deletions
4987681  the weight of the fog                               -> added all the .fog files
f7c00b3  Create retrospective.c
0926e96  added core memories  "missed this time ... its fading from me"  -> the_golden_age.jpg
deab4f3  Initial commit
```

The last commit had "wiped" a C file, so I pulled it back out of the previous commit:

```bash
git show 4987681:retrospective.c
```

It was a small program converting between signed integers and two's complement binary strings, and the very last line was:

```c
// miss the days when people cared about optimizing there code ...spooky{the_g00d_ (1)
```

That was fragment **(1)**: `spooky{the_g00d_`

There was also a loose object (`3b09921d...`) outside the pack, which looked promising as a dangling "lost" tree. After diffing it, it turned out to be just the tree of the current HEAD (all the fog files without `retrospective.c`), so it was a dead end. `git fsck --unreachable` didn't find anything else either.

## Finding the Rest

While going through the `.git` folder by hand, I found a file that git itself doesn't create: `.git/errored_space.txt`

```
61, the year the memories cuts through the fog... th3_void} (3)
```

That gave me fragment **(3)**: `th3_void}`, plus a hint pointing to **61**.

I checked both line 61 of `fog.fog` and the hidden `.fog61.fog`. While doing that, I also tried decoding every hash from hex to bytes to see if any of them was readable text instead of a hash. Exactly one was:

```
.fog61.fog: 7468655f6c3073745f406e6420283229
         -> the_l0st_@nd (2)
```

So the 150 other "hashes" were just random fog, and `.fog61.fog` was fragment **(2)**: `the_l0st_@nd`

## Putting It Together

```
(1) spooky{the_g00d_
(2) the_l0st_@nd
(3) th3_void}
```

Fragment 3 started with a space (`... th3_void}`), and the file was literally called `errored_space.txt`, so I took the space as the "error" and replaced it with an underscore like the rest of the flag.

🚩

```flag
spooky{the_g00d_the_l0st_@nd_th3_void}
```
