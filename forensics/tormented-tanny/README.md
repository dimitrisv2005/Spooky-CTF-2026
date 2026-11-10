# Tormented Tanny

**Category:** Forensics

## The challenge

> An image was captured of a vicious beast while guarding his castle. The cameraman may have found just what makes this beast so furious. Unfortunately, the cameraman seems to have gone missing. Maybe the photo contains the answer.

A photo of an angry dog.

## Figuring it out

"Captured", "cameraman", and "the photo contains the answer" all pointed at metadata. Cameras write a pile of fields into a photo (author, comments, description, GPS), so that's where I looked.

The trap here is that Windows' own Properties > Details tab only shows a handful of fields. It gave me `Title = hates_his_`, which is clearly part of a flag but ends mid-word. The rest was hiding in fields Windows doesn't surface.

## Solving it

I ran the image through a full EXIF/XMP viewer (any of exiftool, exif.tools, jimpl.com). The flag was split across three separate metadata fields:

- `PNG:Title` -> `spooky{tormented_tanner_`
- `XMP-dc:Description` -> `hates_his_`
- `IFD0:ImageDescription` -> `vetsulin}`

Stitched together in that order it reads as a sentence. Vetsulin is insulin for diabetic dogs, which is the joke, that's why the dog is furious.

## Flag

```
spooky{tormented_tanner_hates_his_vetsulin}
```

## Takeaway

A flag can be chopped up and scattered across different metadata fields (EXIF, XMP, PNG text chunks). Windows Properties shows only some of them, so always open the file in a proper EXIF tool before deciding a metadata challenge is empty.
