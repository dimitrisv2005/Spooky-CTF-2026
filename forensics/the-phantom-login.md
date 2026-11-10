# The Phantom Login

**Category:** Forensics | **Difficulty:** Medium | **Points:** 250

> It's Halloween night at NJIT. A long-forgotten account has awakened, and something has been taken from the restricted archives. The SOC captured authentication records and web traffic, but most activity appears ordinary. Follow the phantom's trail and recover the message it left behind.

I was given three files:

- `njit_security.csv`: Windows security events (event code, account, source IP, host, result)
- `njit_web.log`: web server access log
- `case_notes.txt`: says that around **03:10 UTC** the SOC saw strange authentication activity, followed by access to an archive resource

Hint: *Correlate the account names, source IP addresses, and timestamps to identify the suspicious sequence.*

## Initial Attempts

Both logs are a few hundred lines of mostly normal traffic from the same handful of users (`apatel`, `bturner`, `jroberts`...) on internal `10.13.x.x` addresses. I first got distracted by a burst of failed logins for **`administrator`** from `198.51.100.66` between 01:48 and 01:54. It looked like a brute-force attack, but none of those attempts succeeded and it happened more than an hour before the time in the case notes. It was a decoy.

## Following the trail

Following the hint, I looked for an account and IP that don't fit the normal pattern. One account stands out: **`evelyn.graves`**, the "long-forgotten account". It's the only user ever seen from **`203.0.113.77`**, an external address.

Lining up her events from both logs in time order:

| Time (UTC) | Source | Event |
|---|---|---|
| 03:10–03:12 | Security log | 8 × **4625** failed logins, status `0xC000006A` (wrong password), so someone is guessing |
| 03:14 | Security log | **4624** successful login using **NTLM** (every other user uses Negotiate), `LogonID=0xB130` |
| 03:15 | Security log | **4672** special (admin) privileges assigned to the same session `0xB130` |
| 03:16 | Web log | `GET /archives/` |
| 03:17 | Security log | **5140** access to the hidden share `\\BW-FS01\Archives$` (session `0xB130`) |
| 03:18 | Web log | `GET /archives/records?year=1893` |
| 03:19 | Web log | `GET /archives/export?note=c3Bvb2t5e3RoZV9naG9zdF9sZWZ0X2FfdHJhY2V9` |

The `LogonID=0xB130` is what ties it together: the same session logs in, gets admin rights and opens the archive share. The last request carries a `note` parameter that looks like Base64.

## Finding the solution

```bash
echo c3Bvb2t5e3RoZV9naG9zdF9sZWZ0X2FfdHJhY2V9 | base64 -d
```

🚩

```flag
spooky{the_ghost_left_a_trace}
```
