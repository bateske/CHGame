# Pixel art: the conventions

Every sprite and picture in this repository is pixel art: each pixel is
placed on purpose. This page is the craft's rule book, condensed from the
community's canonical teaching (Cure's Pixel Art Tutorial, Saint11's
tutorials, Michael Azzi's *Pixel Logic*; see the end) and fitted to this
platform: a 128x128 panel, the games' 16-colour HOUSE palette, the menu
pictures' 11 colours plus four ([cover-art.md](cover-art.md)), and sprites
stored as runs of one colour (`sprite4`), where every change of colour
along a row costs a byte.

[cover-art.md](cover-art.md) is the house look built on these rules.
`tools/artkit` enforces what a program can check: `artkit.lint` on menu
pictures (colours, edges, doubled pixels, specks) and `artkit.craft` on
anything, sprites included (orphans, jaggies):

```
python -m artkit.craft SPRITE.png ...
```

A rule here is a default, not a law: each has exceptions, and the test is
always how it reads at 1x on the panel.

## Geometry: lines and curves

1. **Straight lines are clean.** A horizontal or vertical line is one pixel
   thick, with no gaps and no bulges.
2. **Curves step evenly.** Along a diagonal or a curve, the lengths of the
   runs (the pixels between two steps) change smoothly: a curve from flat
   to steep goes 4, 3, 2, 1, 1, then 2, 3 rows; a diagonal holds one length
   (2, 2, 2) or alternates evenly (1, 2, 1, 2). A run that breaks the order
   is a **jaggie**:

   ```
   BAD   ######..........     runs 6, 1, 6: the 1 is a kink
         ......#.........
         .......######...

   GOOD  ######..........     runs 6, 3, 2, 1: the curve steepens evenly
         ......###.......
         .........##.....
         ...........#....
   ```
   `artkit.craft` lists them on silhouettes and colour clusters.
3. **Circles are symmetric.** Mirror halves and quadrants must match. Small
   circles are hand-placed, not taken from an ellipse tool: at 5-12 pixels a
   circle is a few chosen runs (a 6-wide coin: `.####.`, `######` x2,
   `.####.`). Tiny ones may be diamonds or octagons.
4. **Perspective is consistent.** One set of axes per scene; isometric art
   on a strict 2:1 grid (CHChess, CHCheckers, CHTicTacToe). A chip seen from
   the side is an ellipse squashed by the same ratio everywhere in a game.
5. **No accidental corners.** A one-pixel line drawn freehand grows L-shaped
   2x2 corners; remove them (artkit's `ink` draws without them), or keep
   square corners everywhere on purpose.

## Clusters

6. **Colour in clusters.** Pixels of one colour form solid patches that
   describe a shape. A lone pixel (an **orphan**) reads as noise, unless it
   is a deliberate glint, a star or a pip; `artkit.craft` and `artkit.lint`
   list them. Ask of each: does this pixel carry information?
7. **No banding.** Two edges that follow each other step for step (an
   outline hugging a shape with a parallel staircase of shading inside it)
   show the grid as a fat stair. Offset one of them.
8. **Silhouette first.** A sprite must read as a shape in one colour before
   detail goes in: silhouette, then big colour masses, then the features
   that identify it, then fine detail.

## Colour

9. **A small palette, reused.** Build ramps (dark to light) from few
   colours and use them everywhere; a new colour only where a ramp has a
   gap. Here the palette is fixed: the games share HOUSE, so ramps are
   made from it (INK, NAVY, BLUE, CYAN, WHITE; INK, WINE, RED; INK, WOOD,
   GOLD; INK, FELT_DK, FELT, FELT_LT; INK, SILVER, WHITE).
10. **Shift hue, not just value.** Shadows cooler and more saturated,
    lights warmer: a red chip's shadow goes WINE, not grey.
11. **Contrast carries it.** The subject must part from its background in
    value. If it doesn't, add an outline, a rim of light, or darken the
    ground.

## Edges, anti-aliasing and outlines

12. **Anti-alias only where it helps.** Soften the ends of long runs on a
    curve with one in-between colour; never anti-alias a straight line or a
    clean 45 degree line. Too much makes edges blurry.
13. **An AA pixel is an in-between.** Its value sits between the two areas
    it joins.
14. **Outline selectively.** A dark outline helps a sprite against a busy
    ground; inside the shape, or on the lit side, a darker shade of the
    colour beside it often reads better than black. On this panel, sprites
    over the felt and the navy wall usually keep an INK outline for
    contrast, coloured lines inside.

## Dithering

15. **Dither to blend, not to fill.** A checker between two neighbours on
    a ramp makes a soft transition or a texture (felt, smoke, sky). If more
    than about a quarter of an area is dithered, a midtone would do better;
    a dithered pattern must still read as a tone at 1x. On the games'
    sprites a dither costs a byte per pixel (each pixel is its own run),
    so it is rare there.

## Light and shading

16. **One light.** The house key light comes from the top left; shadows
    fall to the lower right, on every object in a picture.
17. **No pillow shading.** Never shade in rings that follow the outline
    (dark rim, light middle): it ignores the light. Shade by form: the lit
    side, the shadow side, a sharp or briefly dithered terminator between.
18. **Flat is flat.** A plane takes one colour (two at most); ramps belong
    to curved forms. A chip's top is a plane; its rim is a cylinder.
19. **Highlights, rims and cast shadows earn their place**: add one only
    where it makes the form or the material read.

## Sprites and animation

20. **Readable at 1x.** Judge every sprite at its real size on the panel,
    on its real background (the felt, the wall). If it doesn't read, simplify
    and add contrast before adding detail.
21. **Frames hold their shape.** In an animation, clusters move a pixel at a
    time and keep their mass; nothing jumps unless the motion is fast on
    purpose.
22. **One family per game.** Sprites that sit together (chips, cards, the
    dealer) share a light, an outline rule and a level of detail.

## Tiles and scenes

23. **Tiles join seamlessly**: test a 2x2 arrangement. Stagger patterns so
    the grid doesn't show.
24. **One palette per scene**, and detail only where the eye should go;
    keep big shapes flat.

## Scaling and files

25. **Integer scaling only**, nearest neighbour: previews at 2x, 3x, 4x,
    never 150%. (CHFour draws the dealer at 2x on the panel: every pixel
    becomes a 2x2 block, a known exception, and his art is judged at 2x
    there too.)
26. **Keep the source.** Art here is a recipe (`tools/cart.py`,
    `tools/assets.py`) or text art, generated into PNGs and arrays: edit the
    source, never the output. PNG only, never JPEG.

## The workflow

Reference and concept, then the canvas and palette, then silhouette and big
clusters, then clean the outlines (jaggies, corners), then base colours,
then light and shadow, then AA and texture, sparingly, then polish (glints,
small accents), then export at integer scale and check at 1x on the real
background (the simulator: `chgame run`).

## Sources

| Source | Author | Notes |
|---|---|---|
| *The Pixel Art Tutorial*, Pixel Joint (2010, updated 2014) | Logan "Cure" Tanner | The classic: clusters, AA, jaggies, dithering, banding, pillow shading, palettes. https://pixeljoint.com/forum/forum_posts.asp?TID=11299 |
| *Pixel Art Tutorials* | Pedro "Saint11" Medeiros | Hundreds of short illustrated lessons (lines, clusters, AA and banding, shading, colour). CC BY 4.0. https://saint11.art |
| *Pixel Logic: A Guide to Pixel Art* | Michael Azzi | A visual book on lines, AA, colour, readability, dithering, sprites, animation. Commercial. https://pixellogicbook.com |
| *Pixel Art for Game Developers* (CRC Press, 2017) | Daniel Silber | A text-led book on sprites, animation and tiles. Commercial. |
| *Pixel art tutorials* index | Lospec | Hundreds of tutorials tagged by topic. https://lospec.com/pixel-art-tutorials |
