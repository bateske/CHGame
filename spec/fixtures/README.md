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

## bad/

One cart per error code, each named after it, each breaking that rule only:
`not-a-zip`, `bad-zip`, `no-manifest`, `bad-json`, `schema-version`,
`missing-field`, `bad-field`, `missing-file`, `bad-id`, `duplicate-id`,
`bad-title`, `bad-folder`, `bad-device`, `binary-size`, `bootloader-image`,
`bad-sd-path`, `sd-conflict`, `bad-image`, `bad-background`, `bad-launch`.

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
