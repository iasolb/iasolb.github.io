# Portrait crops for iansolberg.us

Source: Ian sent the photo in chat 2026-08-27. `portrait-master.jpg` is the
upright master, downscaled to 2400x3200 (the original was 5712x4284 and 3.4 MB,
which no web page needs).

## NO FILTERS ON HIS FACE. EVER. (Ian, 2026-08-27)

His words, shown three colour-graded versions: **"not sure why u put so many
filters on my face"**. He was right to push back and nobody had asked for it.

- **Cropping and resizing are fine. Colour grading is not.** No desaturation, no
  warm or cool tint, no contrast curve, no duotone, no "editorial treatment".
- **Two attempts were made and both are deleted, not kept as options.** A full
  duotone mapping highlights to parchment came out washed and sickly on skin;
  a subtler version (saturation 0.55, warm screen blend, contrast 1.12) still
  read as a filter to the person in the photograph, which is the only opinion
  that counts.
- **The general form of the mistake:** a treatment nobody asked for, applied
  because it suited the layout, to a picture of him. If a change to his likeness
  is not requested, do not make it.

## The rotation trap, and it will recur with any phone photo

**The original was stored SIDEWAYS with EXIF orientation tag 6**, meaning the
pixels are rotated and only a tag says to turn them. Browsers mostly honour that
tag; resize pipelines, CSS backgrounds and canvas mostly do not, so a naive
downscale would have published him on his side. Every file here has the rotation
baked into the pixels and no orientation tag. **Any new derivative must come from
`portrait-master.jpg`, never from the phone original.**

## The crops

Centred on the face (eyes at a stated fraction down the frame), not
centre-cropped. Face landmarks used: horizontal centre 0.513 of width, eye line
0.346 of height.

| file | displayed at | eyes at | for |
|---|---|---|---|
| `byline-240.jpg` | 62px circle | 0.44 | the masthead byline portrait, which is what shipped |
| `inset-460.jpg` | 96x117 | 0.38 | portrait inset with text wrap |
| `hero-1560.jpg` | full width x 210 | 0.45 | full-width hero band |

**Known limitation of the source photo:** the background is a bright
architectural ceiling. It competes with the face at wide aspect ratios, so the
hero band is the weakest of the three and Ian ruled that layout out. A
full-width photo-led design wants a different picture, shot wider against a
plain or dark background.
