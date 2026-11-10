# Cleithrophobia


> You are stuck inside of the Enterprise with no way out. The rest of the crew has gone missing. They need help finding a way back to a Federation outpost but the ship is stuck dead in space. Maybe the packet file they have can find a way to start the ship.

I was given `Cleithrophobia.pcap`, a packet capture with 2,000 packets.

Hint: *Look for the traffic that changes the state of the ship.*

## Initial Attempts

I first ran `strings` and grepped for `spooky` and `{`. The only hits were hostnames like `lcars.starfleet.fed{`, nothing useful.

Next I got an overview of the traffic with `scapy` (Wireshark's *Statistics → Conversations* shows the same thing). It's full of noise:

- ~600 packets of TLS on port 443 (encrypted, can't read)
- FTP logins from `scotty`, `sulu`, `chekov`, `spock`, `uhura` with their passwords in plain text
- ICMP pings carrying `transporter_pattern_buffer_...`
- UDP chatter like `stardate=46910.4`, `sensor_sweep=sector-61`, `heartbeat=stardate-6190`
- lots of `status=green;deflector=zsoNLFooed0=` and `warp_core_telemetry=czwh+0HnuvmuvQ==`

The `deflector=` and `warp_core_telemetry=` values look like Base64, so I tried decoding a few, but they're just random bytes. These are decoys.

## Finding the solution

The hint says to look for traffic that **changes the state** of the ship. Every HTTP request in the capture is a `GET` (it reads something, like `/bridge/status` or `/sensors/long-range`) except one: a single **`POST`** in packet 403.

```
POST /bridge/ignition HTTP/1.1
Host: bridge.ncc1701.starfleet.local
Authorization: Basic Y2FwdGFpbi5raXJrOkVudGVycHJpc2UtMTcwMS1B
Content-Length: 0
```

The Basic auth value decodes to `captain.kirk:Enterprise-1701-A`. The server's response in packet 404 is the important part:

```
HTTP/1.1 200 OK
Content-Type: text/plain
X-Bridge-Telemetry: deflector_part1=U3Bvb2t5e0JlMA==
X-Deflector-Status: deflector_part2=bV9NZV9VcF9TYw==
X-Warp-Core-Reading: deflector_part3=MHR0eV8yMjY2fQ==

IGNITION AUTHORIZED - WARP CORE PREPARING
```

The flag is split across three custom headers, each Base64-encoded:

| Header | Base64 | Decoded |
|---|---|---|
| `X-Bridge-Telemetry` | `U3Bvb2t5e0JlMA==` | `Spooky{Be0` |
| `X-Deflector-Status` | `bV9NZV9VcF9TYw==` | `m_Me_Up_Sc` |
| `X-Warp-Core-Reading` | `MHR0eV8yMjY2fQ==` | `0tty_2266}` |

```python
import base64
parts = ['U3Bvb2t5e0JlMA==', 'bV9NZV9VcF9TYw==', 'MHR0eV8yMjY2fQ==']
print(b''.join(base64.b64decode(p) for p in parts))
```

In Wireshark the filter `http.request.method == "POST"` finds it immediately, and *Follow → HTTP Stream* shows the response headers.

🚩

```flag
Spooky{Be0m_Me_Up_Sc0tty_2266}
```
