# Arachnophobia

I was given the SpookyCTF 2026 logo as a PNG (a green spider sitting on a web, with a padlock shield on its back). The challenge text was:

> Something about the SpookyCTF logo feels off… like something's tangled in the webs

## Initial Attempts

After the Haunted Portrait challenge, my first guess was more bit-plane steganography, but before trying that I went through my usual file forensics checklist.

## Standard Forensics

`file` said it was a normal PNG and `strings` didn't show anything useful. Then I listed the PNG's chunks. A PNG file is a series of chunks that always ends with an `IEND` chunk, and image viewers stop reading at `IEND`:

```
[PNG signature] → IHDR → IDAT ... IDAT → IEND
```

Here, though, the file kept going: there were **214 extra bytes after `IEND`**, and they started with:

```
PK\x03\x04 ... flag.txt
```

`PK\x03\x04` is the signature at the start of every ZIP file. Someone had appended a ZIP archive to the end of the image, probably with something like:

```bash
cat logo.png secret.zip > logo_with_zip.png
```

This works because ZIP readers look for the archive from the **end** of the file, so the PNG part in front doesn't bother them. The file is a valid image and a valid ZIP at the same time. That trick is called a polyglot.

## Finding the solution

Any of these will extract it:

```bash
binwalk -e logo.png
unzip logo.png
7z x logo.png
```

I did it in Python:

```python
import zipfile, io
d = open('logo.png', 'rb').read()
z = zipfile.ZipFile(io.BytesIO(d[d.find(b'PK\x03\x04'):]))
print(z.namelist())          # ['flag.txt']
print(z.read('flag.txt'))
```

The flag is also a pun: a spider has 8 legs, and the secret was a zip.

🚩

```flag
spooky{8_l3gs_4nd_4_z1p}
```
