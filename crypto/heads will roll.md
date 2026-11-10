# Heads Will Roll
 *Crypto*

> While chasing Ichabod Crane through Sleepy Hollow, the Headless Horseman got as close as he could, then threw his head! While rolling, rolling, rolling, rolling, through the air, his pumpkin head shouted…what? His perfect aim knocked Ichabod to the ground near the rails, but what did he say?

I was given `pumpkin_head_message.txt`:

```
Etu_taip5_w5n_hpmnw_hlgsdso{lyh0_d}jyi_piihef_ne_oy3p0lh4oskt_i:k3l3
```

## Reading the riddle
The flavour text is the whole key:

- *"knocked Ichabod to the ground **near the rails**"* → this is a **Rail Fence cipher**.
- *"**rolling, rolling, rolling, rolling**"* → the word "rolling" appears **four** times → **4 rails**.

## Decoding
Running a rail fence decode with 4 rails:

```python
def railfence_decode(ct, rails):
    n = len(ct); pat = []; r = 0; d = 1
    for i in range(n):
        pat.append(r)
        if r == 0: d = 1
        elif r == rails - 1: d = -1
        r += d
    order = sorted(range(n), key=lambda i: pat[i])
    out = [None] * n
    for ch, pos in zip(ct, order): out[pos] = ch
    return ''.join(out)

print(railfence_decode(open('pumpkin_head_message.txt').read().strip(), 4))
```

Out comes the horseman's shout with the flag baked in:

```
Enjoy_this_pumpkin_with_the_flag_inside:_spooky{5l33py_h0ll0w_h34d5}
```

🚩

```flag
spooky{5l33py_h0ll0w_h34d5}
```
