# Conformance fixtures

Carts that every implementation of [../chgame.md](../chgame.md) and
[../card.md](../card.md) must read and prepare as `expected/` says. Made by
[tools/chcart/fixtures.py](../../tools/chcart/fixtures.py); checked by
`python tools/chcart/fixtures.py --check` (part of chcart's tests).

Every game's program is [src/hello.bin](src/hello.bin), the CHGame library's
Hello example, so an emulator can run any of them.

## good/

| Cart | What it covers |
|---|---|
| `single.chgame` | one game, its licence file, no SD files: the smallest real cart |
| `single-sd.chgame` | one game with SD files in a subfolder, a cart image, an animated GIF and a PNG screenshot, a button |
| `multi.chgame` | seven games: a folder and a folder inside it, a launch game two levels down, the cart's background and colours, a folder's background, a file two games share, two games called WORDS (in different folders), one called CON (a Windows device name), a title longer than the menu shows, an author too long for the CHG header |
| `warnings.chgame` | readable, with every warning: an unknown key, a stray file, a 21-character title, a title the menu cannot show, an image that covers the save pages |
| `pictures.chgame` | the visual menu's pictures: the cart's cover and about page, two folders' covers (one two levels down), two games' pictures, a folder with neither |
| `system.chgame` | `menu.systemImages`: three of the menu's own screens replaced (installed, folder, error-4) and an about page; the defaults fill the other slots of `SYSTEM.PIC` |
| `extension.chgame` | a cart from the web tool before `menu.systemImages` existed, written raw: `x-chgame-web` version 1 names two system screens, `menu.systemImages` names one of them differently (the official field wins, with `extension-conflict`), and an `x-other-tool` key rides along, warned about by nobody |

## bad/

One cart per error code, each named after it, each breaking that rule only:
`not-a-zip`, `bad-zip`, `no-manifest`, `bad-json`, `schema-version`,
`missing-field`, `bad-field`, `missing-file`, `bad-id`, `duplicate-id`,
`bad-title`, `bad-folder`, `bad-device`, `binary-size`, `bootloader-image`,
`bad-sd-path`, `sd-conflict`, `bad-image`, `bad-background`, `bad-launch`,
`full-folder` (241 games at the top level, sharing one binary).

## expected/

`<name>.json` for each cart:

- **A bad cart:** `{"errors": [codes]}`.
- **A good one:**
  - `warnings`: the codes;
  - `games`: each game's id, title and folder, the size and SHA-256 of its
    binaries, and the SHA-256 of each SD file;
  - `launch`;
  - `card`: every file runtime preparation writes, with its size and
    SHA-256.

Nothing in it depends on where a writer put files inside the ZIP. An
implementation conforms when it gives the same codes, the same games and
the same card, byte for byte.

## backup/

Cards to back up (card.md, "Backing up a card"): each `<name>.zip` holds a
card's files at their paths. `expected/backup/<name>.json` is what backing up
the whole card must give.

| Card | What it covers |
|---|---|
| `multi.zip` | `good/multi.chgame` as prepared: folders, the launch game two levels down, the cart's colours (`mark` comes back as RGB565 gives it: `#FF8100`), its background and a folder's, a file two games share, two games called WORDS |
| `pictures.zip`, `system.zip` | the same for `good/pictures.chgame` and `good/system.chgame`: the cover, the about page, folder covers, the menu's own screens; the defaults left out |
| `edited.zip` | a card changed by hand: an SD file gone (`sd-missing`), a shared one changed (`sd-changed`, for both games), a game moved into another folder (in no `MENU.IDX`: it sorts after the indexed ones), a game copied into a folder (`renamed-id`: `words-2`), a CHG file without a record (`no-record`), one with its payload damaged (`bad-chg`: left out), one with its record damaged (`bad-record`: backed up from its header), a file at the root no game names (not backed up) |
| `old.zip` | `good/single-sd.chgame` prepared before records: the game from its header and picture, no SD files (`no-record`) |

`expected/backup/<name>.json`:

- `warnings`: the codes;
- `games`, in the menu's order: id, title, folder, the record's text keys,
  the size and SHA-256 of the binary, the SHA-256 of each SD file and licence
  file, and `picture`: the SHA-256 of its `cartImage` made into a picture
  (card.md, step 7), or `null` (none, or one that breaks the picture rule);
- `launch`;
- `menu`: the colours, and the SHA-256 of the background, the cover, the
  about page, each system screen and each folder's background and cover,
  each as runtime preparation encodes it (so a PNG encoder's choices do not
  matter), `null` where the cart has none;
- `sameCard`: whether preparing the backup gives the card's files again,
  byte for byte (`true` for the three cards as prepared).
