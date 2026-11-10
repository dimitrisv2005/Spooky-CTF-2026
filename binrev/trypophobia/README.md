# Trypophobia

 *Binrev — 75 points*

A compiled Java `.class` file, pitched as "classic reverse engineering." The program reads a string, runs it through a `check()` method, and prints `Correct!` if it validates.

## Reading the bytecode

```bash
javap -c -p Trypophobia.class
```

`check()` validates the flag character by character. It requires the input to be exactly **34 characters** long, and for each position it enforces one of **four arithmetic/XOR patterns** built from per-position constants.

The bytecode is sprinkled with `dup` / `pop` / `swap` instructions as **obfuscation** — they shuffle the operand stack around but never change the value that actually gets computed.

## Emulating instead of tracing

Tracing 34 positions of hand-obfuscated bytecode by hand is miserable, so I wrote a small Python **stack-machine emulator** that parses the disassembled `check()` bytecode, then for each position brute-forces printable ASCII until it finds the character that satisfies that position's constraint:

```
for i in range(34):
    for c in printable_ascii:
        if emulate_check_constraint(i, c):   # run that position's bytecode slice
            flag[i] = c
            break
```

The first version mishandled `invokevirtual` — it popped from the operand stack even when the stack could be empty, which threw the emulation off. Once I fixed the stack-pop handling for that one opcode, the solver spat out a clean 34-char string.

## Verifying

Feed the recovered string back into the real program:

```bash
echo 'spooky{ever_reversed_java?A67b_91}' | java Trypophobia
# -> Correct!
```

🚩

```flag
spooky{ever_reversed_java?A67b_91}
```
