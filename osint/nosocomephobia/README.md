# Nosocomephobia


I was given an audio file called `cassetterecording.mp3` and a black-and-white photo of a town on a hill with a ruined castle on top. According to the story, both were found in a bottle that washed up on the shore. The task was to find out **where** and **when** the recording was made.

Flag format: `spooky{location_name.year}`

## Initial Attempts

The challenge said the cassette "sounded like simple beeping". Short and long beeps made me think of Morse code straight away, but I didn't want to sit there writing down dots and dashes by ear, so I went looking for a way to decode it automatically.

## Decoding the Morse

I converted the MP3 to a mono WAV with `ffmpeg` and wrote a small Python script. It splits the audio into tiny windows, measures the loudness of each one, and marks it as "beep" or "silence". Then it measures how long each beep and each gap lasts:

- short beep → `.`
- long beep → `-`
- short gap → next symbol
- medium gap → next letter
- long gap → next word

```python
import wave, numpy as np

w = wave.open('a.wav')
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
f = 80
e = np.array([np.abs(x[i:i+f]).mean() for i in range(0, len(x)-f, f)])
on = e > (e.max() + np.median(e)) / 2
# ...group the on/off runs by length and map them through a Morse table
```

The message it gave was:

```
HELLO?? HELLO? I HAVE NO RECOLLECTION OF WHERE I AM CURRENTLY...
THE ONLY THING THAT I HAVE WITH ME, IS THIS PICTURE OF MY CITY WHICH HAS BEEN PASSED DOWN FOR GENERATIONS...
IT FEELS UTTERLY COLD IN MY ROOM... EVERY OTHER MINUTE I HEAR ANOTHER SHOCK FOLLOWED BY A SCREAM...
EVERYONE HERE IS REFERRED TO AS A "PATIENT"...
SOME "DOCTOR" SPOKE ABOUT THE WEEKLY EVENTS THAT ARE ON-GOING, WHERE ME AND OTHERS WOULD BE ATTENDING
A SCREENING OF AN EDUCATIONAL FILM, IN ROOM MALE 2?... IF ANYONE HEARS THIS, PLEASE SAVE ME...
```

So the speaker is a patient in an asylum (the "shocks" sound like electroconvulsive therapy), and the photo shows their home town.

## Finding the Location

The photo shows a town climbing up a hill with a ruined castle on top. That matches **Denbigh** in north Wales and its castle. Denbigh is also home to the **North Wales Hospital**, which opened in 1848 as the Denbigh Asylum. Its wings were split into male and female sides, so a ward called "Male 2" fits, and former staff rescued an ECT machine from the building before it closed.

## Finding the Year

The remaining clue was the "weekly events" and the "educational film" screening. I found an [Archives Wales article about entertainment for the hospital's patients](https://archives.wales/2019/07/11/entertaining-patients-in-the-north-wales-hospital/). It includes a scanned **weekly bulletin of patient activities**, captioned as being from **1966**. That's the only weekly events schedule in the article, so I took 1966 as the year.

🚩

```flag
spooky{north_wales_hospital.1966}
```
