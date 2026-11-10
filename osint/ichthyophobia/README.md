# Ichthyophobia

 *OSINT / GEOINT — 280 points · medium*

> I've been having a recurring nightmare since I was a child. I don't know why I keep seeing it over and over, but I vividly dream about this random place I've never been to. It always ends with me falling into this koi pond. The thought of being surrounded by the fish has been bugging me for a long time. Now, as an adult, I've decided to draw what I see, but no one understands why I would be afraid of this place. I feel like I'm losing my mind. I don't remember going here, but it feels so... familiar. I don't know... Can you figure out the name and location of this plaza?

**Author note:** the flag is the name of the **most-reviewed location at this plaza**, in all uppercase, no diacritics, with underscores instead of spaces.

What I got was an **anime-style drawing** of an open-air plaza: a koi pond with stepping stones and a little planted island, Portuguese storefront signs ("DROGARIA", "DECIO", "VARIEDADES STORE"), and a tiled-roof courtyard. So two jobs: geolocate the plaza from a *drawing*, then find the single most-reviewed place in it.

## Why the obvious approach fails

Throwing the whole picture into a reverse-image search gets you nowhere — it's hand-drawn in an anime style, so image matching latches onto the art style instead of the real place. Text searches on "koi pond shopping Brazil" just drown you in generic malls (Shopping Carpina, Downtown Barra da Tijuca, a few Florida malls — all wrong).

## What actually worked — crop, don't search the whole thing

The move is to **feed Google Lens only one small, distinctive, real-looking piece** of the drawing, not the whole scene. I cropped **just the island** — the rocks, the single tree, and the little restroom/toilet building behind it — and dropped that into Google Lens.

That one crop was enough: Lens surfaced the **actual store / rest-stop** the island was drawn from. The anime styling stops mattering once you isolate a feature with a real-world twin; Lens matches the layout of the rocks + tree + building straight to photos of the real spot.

## Pinning it down

The hit pointed at a **"Décio"** highway rest-stop complex in Brazil (the blue "DECIO" sign in the drawing was a real brand all along). From there I went to **TripAdvisor**, searched the place name, and confirmed the exact location — a **Décio** *posto* on the **BR-050, Uberlândia, Minas Gerais**.

## Getting the flag format right

The flag is the **most-reviewed location** at that plaza — uppercase, no diacritics, underscores for spaces:

- the place is the Décio complex at Uberlândia →
- `Uberlândia` → `UBERLANDIA` (drop the diacritic),
- spaces → underscores,
- and the listing name is **Posto** (Google / review-platform naming), not "Post" — matching the exact spelling is what makes it validate.

🚩

```flag
POSTO_DECIO_UBERLANDIA
```

**Takeaway:** against a hand-drawn geolocation challenge, don't reverse-search the whole image — crop one real-world-looking detail (here the rock island with the tree and the restroom behind it) into Google Lens, then confirm the exact listing name on a review platform like TripAdvisor or Google Maps, watching the spelling (`POSTO` not `POST`), the underscores, and the diacritics the flag format demands.
