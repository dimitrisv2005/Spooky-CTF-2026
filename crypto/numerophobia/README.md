# Numerophobia

 *Crypto / Encoding*

> I went exploring the house of the crazy old man on the corner of the street. He disappeared last weekend… last seen walking out at midnight screaming random numbers in tongues never spoken before. On the way to the stairs I almost tripped over a stack of books, one was about **dyslexia** I think. For some reason **every other step was missing and marked with a 13** on the wall. Taped on the wall was a piece of paper…

The file `numerophobia.txt` is three lines of space-separated numbers:

```
23 50 65 50 65 ... 50 65
138 50 65 95 123 51 64 98 108 53 ... 128
63 52 63 52 63 52 ... 63 52
```

## Reading the riddle
Three clues, three operations:

- *"screaming random numbers"* → the numbers are **ASCII codes**.
- *"every other step was missing and marked with a 13"* → **subtract 13 from every other value** (starting from the first).
- *"a book about **dyslexia**"* → the result reads **backwards**, so **reverse** it.

## Decoding
```python
n = list(map(int, open('numerophobia.txt').read().split()))
b = [v - 13 if i % 2 == 0 else v for i, v in enumerate(n)]
s = ''.join(chr(x) for x in b)
print(s[::-1])
```

The first and third lines decode to `4242424242…` padding (a nod to the answer), and the middle line gives:

```
spooky{th3_4n5w3r_h45_4lw4y5_b33n_42}
```

🚩

```flag
spooky{th3_4n5w3r_h45_4lw4y5_b33n_42}
```
