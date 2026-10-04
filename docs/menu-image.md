# The menu's picture: changing it

The SD menu draws its list over one picture, 128x128 pixels, that comes from
the SD card. The CHGAME logo at the top is part of that picture, not of the
bootloader. So changing the picture changes everything you see behind the
list: the logo, the title, the colours, the art.

(This is the list menu's picture. The visual menu shows other pictures: the
card's cover, the folders' covers and each game's box art, made the same
way with `chgame picture`: [visual-menu.md](visual-menu.md).)

![The menu on the default picture, on a picture of a card's own, and on a card with none](../platform/bootloader/docs/menu_cards.png)

`chgame background` does the work: it turns any image into one the menu can
show, draws the menu on it so you can see the result on the PC, and puts it
on a card. (`pip install -e .` in the repository root gives the `chgame`
command; `python tools/chgame.py background ...` is the same.)

## The layout

```
 y   0 +------------------------------+
       |  the picture's own: the logo, |   rows 0-19: the menu never draws here
 y  20 +------------------------------+
       |  BACKGAMMON          (bar)   |   rows 20-119: the list, ten rows of ten
       |  BLACKJACK                   |   pixels. Titles in cream from x = 8; the
       | ▌CHESS                       |   selected row is a bar across the whole
       |  ...                         |   width in the rainbow colour; a red chip at
       |  APPS                      > |   x = 2-4 marks the installed game, `>` at
 y 120 +------------------------------+   x = 122 a folder
       |  the picture's own: hints     |   rows 120-127: the menu never draws here
 y 127 +------------------------------+
```

Messages (INSTALLING, ERROR n, USB UPLOAD) are boxes over rows 36-87.

- **The rainbow.** Paint anything in pure magenta, **#FF00FF**, and the menu
  draws it in one colour that turns through the rainbow, like the default
  logo and the selection bar. On a bootloader built in the Static style
  (*Tools > Bootloader > SD Text Menu (Static)*) nothing turns: the
  picture is shown exactly as painted, magenta included, and the selection
  bar is magenta.
- **Colours.** Besides magenta, a picture holds 11 colours. More are
  reduced to 11 for you; a picture with few, flat colours looks best.
- **The palette.** The default picture is an indexed PNG whose 16 colours
  are laid out as the menu's: 0-10 are the picture's own (a starter set:
  change them to whatever you like), 11-14 the menu's text, disabled,
  selected-text and mark colours, 15 the rainbow's magenta. A picture need
  not be indexed, though: any PNG that follows the rules above is taken.
- **Readable titles.** Keep rows 20-119 dark and plain behind the text, or
  change the text's colour (step 4).

## Step by step

1. **Start from the default** (or skip this and use any picture you like):
   ```
   chgame background --template my-menu.png
   ```
   This writes the default picture: black, the CHGAME logo in magenta at the
   top, the key hints at the foot.

2. **Edit it** in any paint program: Aseprite, GIMP, Photoshop, Paint.
   - Work at 128x128 and zoom in. Change the logo or write your own title in
     rows 0-19, and put art anywhere.
   - A photo or a larger picture works too: it is scaled to 128x128. By
     default it is cropped to fill; `--fit contain` adds black bars instead.
     Pixel art at 256, 384 or 512 pixels is scaled down pixel for pixel.

3. **Look at it, with the menu on top**, before it goes near a card:
   ```
   chgame background my-menu.png --preview preview.gif
   ```
   The preview is the menu as the CHGame draws it (the bootloader's own tests
   check that it matches), three times the size, with the rainbow turning
   (`.png` for a still; `--style static` for the Static bootloader). If the picture had to be changed to fit, the command
   says how. `--out ready.png` keeps the changed picture, and `--dither`
   helps photos.

4. **The text's colours, if the picture needs them:**
   ```
   chgame background my-menu.png --preview preview.gif --color text=#FFFFFF --color selectedText=#202020
   ```
   They are `text` (titles, #FFF4D6), `disabled` (a file that is not a game,
   #808080), `selectedText` (the title on the bar, #000000) and `mark` (the
   chip, #D62020). Give the same `--color` options to the commands in step 5.

5. **Use it.** Pick one:
   - **Straight onto a card.** Mount the card on the PC (a card reader, or
     the CHGame's own **APPS > SD CARD READER**):
     ```
     chgame background my-menu.png --card E:\
     ```
     This writes `GAMES/MENU.BG` on the card. Eject the card, and the next
     power-on shows the new picture. Nothing else on the card changes.
   - **In a cart** (a `.chgame` you share), so every card it goes on gets it:
     ```
     chgame cart background mycart.chgame my-menu.png
     chgame cart deploy mycart.chgame --card E:\
     ```
     `--folder "CARD GAMES"` gives one folder a picture of its own instead.
   - **On the repository's casino card.** Save it over
     `tools/sdcard/menu.png`, then run `chgame card` (and deploy
     `out/CHGame-Casino.chgame`, or copy `out/sdcard/`).
   - **For every cart that has no picture of its own** (the platform's
     default): replace `spec/assets/menu-default.png`. This is a change to
     the card format's shared assets: run `python tools/chcart/fixtures.py`
     afterwards, since the conformance fixtures record the default
     picture's bytes.

**No picture on the card** (a card made by hand): the list shows on black,
with no logo.

How the picture is stored on the card, for implementers, is in
[spec/card.md](../spec/card.md) (`MENU.BG`).
