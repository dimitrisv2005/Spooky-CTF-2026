# MIA

 *OSINT / GEOINT*

> We lost direct contact with an informant days ago after someone caught onto their trail. We intercepted a photo that may help determine where they went. The informant wanted to visit a historical site for a drop-off; the individual likely brought them somewhere nearby to hide.

Flag format: `spooky{Site_Name_Here}` — a physical place, not a website.

## The clues

The intercepted image is a composite with three overlay elements:

1. A freshly dug **rectangular pit** with a **"Grabpflege"** sign — German for *grave care / grave maintenance*.
2. An orange **"Harz" tourist card (HarzCard)** with a castle illustration.
3. A **brochure / map** with distance arrows on a rock.

## Following the clues

- The **HarzCard** places this in the **Harz mountains region of Germany**.
- The castle illustration plus "a historical site for a drop-off" points to the **Großer Burgberg** plateau at **Bad Harzburg**, site of the ruins of **Harzburg castle** (built 1065–1068).
- The **"Grabpflege" sign over a freshly dug rectangular pit** says the informant was hidden at a **cemetery** — "somewhere nearby to hide."

The on-site **Burgberg-Seilbahn (cable car) information board** at Bad Harzburg (bad-harzburg.de) confirmed the location and its surrounding destinations.

## Where I burned attempts

This one punished guessing:

- The base photo turned out to be a **decoy** from a Belgian gardening blog with overlay stickers added — don't reverse-image the whole picture.
- `spooky{Kreuz_des_Deutschen_Ostens}` (a memorial cross listed on the board) — **rejected**.
- A Val di Zena whale monument in Italy and a Marburg cemetery flyer — both dead ends.

The key realization: **"Site"** in the flag format is a **place**, not a URL. The volksbund.de / findagrave.com links I'd found were just sources confirming the cemetery's name, not the answer. Pivoting to the cemetery by the Burgberg gave it.

🚩

```flag
spooky{Friedhof_Bad_Harzburg}
```
