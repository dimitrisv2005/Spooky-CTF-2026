# Peering Eyes

 *Forensics / Memory — 793 points*

> Something is watching. I keep feeling like I'm being surveilled while I use my computer.

I was given a ~1 GB LiME memory capture, `spooked2.lime`, taken from a Kali Linux VM, plus a Volatility symbols JSON. The hint: *"Two eyes, two parts to the flag."*

## Setting up Volatility 3

The symbol JSON has to sit at a specific path relative to the `-s` directory, and its filename must match the kernel version:

```bash
python3 -m venv vv && vv/bin/pip install volatility3
# symbols/linux/kali-7.1.5.json  (matches vmlinux-7.1.5+kali-amd64)
```

```bash
vol -s ./symbols -f spooked2.lime linux.pslist
```

One practical note: remote shells I was running this through timed out around ~170 s, so long plugins like `linux.pagecache.Files` have to be backgrounded rather than run in the foreground.

## What's in the capture

The process list turns up a suspicious Python process, **`EYEsee.py`**, using **OpenCV** and **PyAutoGUI** to grab webcam footage and screenshots, shown in a window titled **"eye see you."** That's the surveillance angle from the story — and the hint, *"two eyes, two parts to the flag"*, tells me the flag is split across two sources.

## Part 1 — a string in the Python process

Dumping the Python process's memory and grepping for the flag prefix gives the first half as a plain string constant:

```
spooky{th3y_ar3_
```

## Part 2 — recovered from a webcam frame

The second half was never a string — it was captured *by* the webcam:

1. Extract the raw memory regions belonging to the capture process.
2. Reconstruct the image buffers by working out the correct pixel **width / stride** so the raw bytes line up into a viewable frame.
3. Two webcam frames come out, showing **handwritten notes**.
4. The handwritten note — also sitting in the **X server's memory** — spells the second half:

```
w2tch1ng}
```

## Assembling

```
spooky{th3y_ar3_  +  w2tch1ng}
```

🚩

```flag
spooky{th3y_ar3_w2tch1ng}
```
