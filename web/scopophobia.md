# Scopophobia

> SpookyCTF 2026 — Web
Scopophobia

The challenge dropped me on a single IP with this text:

> After months of unemployment, you finally land a big ol' j-o-b in security. It's minimum wage but hey, the experience is what matters. Though what they didn't tell you was the physical security aspect. Analyze the dashboard and read the source to try to find what they don't want you finding.
>
> `http://18.189.35.130/`

## The dashboard

The landing page is a slick **Network Imaging Control Center (NICC)** security dashboard — monitored-camera counts, a 24h event chart, risk donut, alerts table, all simulated telemetry. Nothing clickable screamed "flag," so I did what the prompt literally told me to and read the source.

Right at the top of the HTML, before anything renders, three comments:

```html
<!-- NICC Imaging Migration Notes -->
<!-- TODO: Legacy camera inventory was excluded from the current monitoring migration. Confirm whether archival feeds were properly retired. -->
<!-- CAM-07 was scheduled for decommissioning but remains registered. -->
```

So there's a camera — **CAM-07** — that's supposed to be gone but is still registered. That's the thing "they don't want you finding." The sidebar also has a **Live Feeds** link pointing at `/feeds/active/cam-01`, which hands me the URL pattern.

## First dead end

Obvious first move: keep the route, swap the number.

```
/feeds/active/cam-07  →  404 "FEED NOT FOUND — camera channel is not registered"
```

Nope. CAM-07 isn't an *active* camera. The route is actually two parts — `/feeds/{class}/cam-NN` — and I'd only been poking at the number, not the class.

## Reading app.js

The page loads `/app.js`. The parts that mattered:

- Feed pages are **server-rendered**; the JS only decorates whatever `.feedpanel[data-feed]` element the server sends. So the interesting data lives in each feed page's HTML, not in the JS.
- There's a hidden reveal mechanism:
  ```js
  // The final feed holds the cryptid frame until playback is reset.
  const revealDelays = poster.hasAttribute('data-timed-reveal') ? [3500, Infinity] : null;
  ```
  A feed marked `data-timed-reveal` plays its first frame for 3.5s, then **freezes on the final frame forever**. Very flag-shaped behaviour.
- The camera `<select>` keeps disabled options (`option:not(:disabled)`), so decommissioned cameras can still be hiding in the dropdown.

Pulling `/feeds/active/cam-01` confirmed the structure: a `data-feed="public"` video feed, and a dropdown listing only `01` (active) and a **disabled "Legacy CAM 03."** CAM-07 had been scrubbed from the UI entirely.

## Following the breadcrumbs

The comment said "archival feeds" and the dropdown said "Legacy," so I swapped the **class** segment instead of the number:

```
/feeds/legacy/cam-07  →  CAM 07 — EAST STAIRWELL
```

That one is a `data-feed="archive"` feed: instead of an `<video>` it's an `<img>` with `data-animation="/feeds/legacy/cam-07/frame"` — an animated GIF. And a fresh comment at the top:

```html
<!-- Service camera directory: /feeds/service/ -->
```

Each archive feed's GIF is a near-black surveillance still that darkens and fades text onto a wall for a split second. Frames are ~200 ms each, so you miss it live — I pulled each GIF and brightened the last frames. Every one hands you the next hop:

| Feed | Reveal text on the wall |
|---|---|
| `/feeds/legacy/cam-07`  | `SERVICE CORRIDOR — SC-12` |
| `/feeds/service/sc-12`  | `MIRROR DOWNLINK: CAM 19` |
| `/feeds/mirror/cam-19`  | `SUB LEVEL B — SLB-04` |

Two things that cost me a couple of 404s:

- Service cameras use an **`SC-NN`** id, not `cam-NN` (so `/feeds/service/cam-07` and friends 404'd until I read `SC-12` off the GIF).
- CAM-19's page carried the last hint I needed:
  ```html
  <!-- Sublevel imaging uses a three-letter directory alongside the other feeds. -->
  ```
  Directories so far: `active`, `legacy`, `mirror`, `service`. The three-letter one is **`sub`**.

## The last camera

```
/feeds/sub/slb-04  →  CAM 04 — SUBLEVEL B
```

This is the **only** feed with `data-timed-reveal` set — the terminal node. It opens on an empty equipment room, then after 3.5s holds the "cryptid frame": a face drops into view and the flag is painted across the floor.

On the held frame the hair covers part of the text, but the GIF has a cleaner frame a beat earlier where the floor text is fully legible. De-animated and brightened, it reads:

```
spooky{Th3_fe3d_goe5_b07H_way$}
```

Reading gotcha: the `0` in `b07H` is a **zero**, not a letter `O`. It's capital-height like the `7` and `H`, and it fits the leet pattern the rest of the string uses (`3`=e, `5`=s, `7`=t, `$`=s).

## Decode

```
Th3   → The
fe3d  → feed
goe5  → goes
b07H  → both
way$  → ways
```

> **"The feed goes both ways."** You think you're watching their cameras — the camera system is watching back.

```flag
spooky{Th3_fe3d_goe5_b07H_way$}
```
