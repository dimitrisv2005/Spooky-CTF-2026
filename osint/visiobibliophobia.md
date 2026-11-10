# Visiobibliophobia

 *OSINT — 491 points · easy*

> Hmmm... it appears that there is a flag on a livestream somewhere on the internet...
> (This is still live btw!)

Clarifications the author gave (not hints):

- OSINT on the admins won't help here.
- The flag is the only thing visible on the livestream — the "format" is literally reading what's on screen and submitting it.
- If you get to the right livestream, you won't need to do anything else.

So the entire challenge is **finding the right livestream**. No link, and a normal Google search gets you nowhere — watching the live solves, people were clearly stuck here. The trick is to stop thinking like a web search engine and start thinking like an **infrastructure** search engine. Enter **Shodan** (Censys works just as well).

## What Shodan / Censys actually are

Both act as search engines for **internet-connected infrastructure**, indexing open ports, service banners, operating systems, cryptographic certificates and hardware types across the IPv4 (and increasingly IPv6) address space.

Where a standard web search engine indexes the *text of web pages*, Shodan and Censys index the raw **network metadata** of hosts exposed to the public internet. That difference is exactly what makes them foundational OSINT tools in both CTF competitions and professional security work — they see things Google never indexes.

### How the pros use them

**Defensive (Blue Team & Risk):**

- **Attack Surface Management (ASM):** organizations constantly lose track of legacy cloud instances, forgotten staging servers and unauthorized deployments (Shadow IT). Continuously querying Shodan/Censys by corporate ASN, SSL-certificate organization fields or IP blocks surfaces unmanaged assets.
- **Exposed credential & database detection:** blue teams scan their own ranges for accidentally exposed protocols (RDP, SMB, Telnet) or unauthenticated databases (MongoDB, ElasticSearch) before attackers find them.
- **Threat hunting & C2 identification:** researchers track malware infrastructure via unique self-signed TLS certs, custom HTTP headers or default banners tied to C2 frameworks like Cobalt Strike, Mythic or Sliver.

**Offensive (Red Team & Pentest):**

- **Zero-touch recon:** assess an external perimeter without noisy scans (like nmap) that trip SOC alerts.
- **Targeted vulnerability scoping:** when a big bug drops (Log4j, MOVEit, a fresh RCE), version-specific dorks like `product:"OpenSSL" version:"..."` quantify exposed targets fast.
- **Attribution & infrastructure graphing:** Censys certificate-graph linkages let you pivot from one known web server to an entire corporate infrastructure ecosystem.

## Solving the challenge

The reason it feels hard is that there's no obvious entry point — but the organizers left the service indexed, and it's branded. Searching the brand name across infrastructure metadata is enough to find it:

1. Go to **Shodan** (or **Censys**) and search **`SpookyCTF`**.
2. The target host is one of the *only* results — often the single result — because that string appears in its banner / certificate / page metadata where these engines index it.
3. Open the host and visit the website. The **livestream is right there** on the page.
4. The flag is the only thing on the stream — read it and submit.

That's the whole thing once you know the tool exists: `SpookyCTF` into Shodan → click the link → read the flag off the livestream. No nmap, no guessing, no brute force — just searching the right index.

### Steps, condensed

1. Search `SpookyCTF` on Shodan / Censys
2. Click the link
3. Read the flag off the livestream and submit

🚩

```flag
spooky{th1s_m1rr0r_i5_w0rldw1d3}
```
