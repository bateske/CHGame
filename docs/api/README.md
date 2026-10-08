# The API reference

The Doxygen reference for every library the board package ships: CHGame,
CHGfx, CHSd, and the core's SPI, Wire and EEPROM. It is published at
**<https://bateske.github.io/CHGame/>** by
[.github/workflows/docs.yml](../../.github/workflows/docs.yml) on every push
to `main` that touches a library or this folder.

| File | What it is |
|---|---|
| `Doxyfile` | the configuration (only what differs from Doxygen's defaults) |
| `mainpage.md` | the front page |
| `groups.dox` | the top-level topics, one per library, with each library's overview |
| `chgfx_fonts.dox` | CHGfx's bundled fonts (their headers are generated, so not commented) |
| `extra.css` | the look: the brand's neobrutalist style ([docs/brand](../brand/README.md)); the logo and the wordmark come from `docs/brand/` |

Everything else comes from the comments in the libraries' headers under
`platform/board/arduino/CHGame/libraries/*/src/`.

## Building it

From the repository root, with Doxygen 1.9.8 or later (the workflow uses
Ubuntu's):

```bash
mkdir -p out/api-docs && doxygen docs/api/Doxyfile
```

Open `out/api-docs/html/index.html`. Warnings go to
`out/api-docs/warnings.log`; the workflow prints them, and a public item
without documentation is one. Without a local Doxygen, Docker does it:

```bash
docker run --rm -v "$PWD:/src" -w /src ubuntu:24.04 sh -c "apt-get update -qq && apt-get install -y -qq doxygen >/dev/null && mkdir -p out/api-docs && doxygen docs/api/Doxyfile"
```

## How the comments are written

The model is the [Arduboy2 reference](https://mlxxxp.github.io/documents/Arduino/libraries/Arduboy2/Doxygen/html/index.html):
everything public says enough for a developer to call it correctly and know
what will happen, and no more. A sentence or two, not an essay.

- **Every public header** opens with a file block: `@file`, a one-line
  `@brief`, then the overview the header already had. Its declarations sit
  inside `@defgroup <name> <Title>` / `@ingroup <library>` ... `@{` ... `@}`
  so they appear under their library's topic.
- **Every public function, method, class, struct, enum, typedef, macro and
  global** has a `@brief` (one sentence: what it does), a `@param` for each
  parameter (units, ranges, what `nullptr` or `-1` means), a `@return` when
  it returns something (what the values mean), and, only when it matters,
  a few lines of details: when to call it, what it costs, side effects.
  `@note` and `@warning` for gotchas, `@see` for its siblings.
- **Struct fields and enum values** take a trailing `///<`.
- **The comment syntax follows the file:** `///` in files written with `//`
  comments (CHGame, CHSd), `/** ... */` and `/**< */` in files written with
  `/* */` (CHGfx, SPI, Wire, EEPROM). Commands are written with `@`, not `\`.
- **Code** is in backticks inline and in `@code` ... `@endcode` blocks.
- **The facts come from the code.** Check a description against the `.cpp`
  before writing it; keep the voice of the existing comments.
- **Comments only.** A documentation change never touches code: a release
  build of every game must stay byte-identical (`sha256sum` the
  `build/release/*.ino.bin` before and after).

The topics:

| Group | Library | Where |
|---|---|---|
| `lib_chgame` | CHGame | `groups.dox`; subgroups `chgame_*` in each `chgame/*.h` |
| `lib_chgfx` | CHGfx | `groups.dox`; subgroups `chgfx_*` in `CHGfx*.h` and `chgfx_fonts.dox` |
| `lib_chsd` | CHSd | `groups.dox`; `chsd_sd` in `SdSpi.h`, `chsd_fat` in `Fat.h` |
| `lib_core` | SPI, Wire, EEPROM | `groups.dox`; `core_spi`, `core_wire`, `core_eeprom` in their headers |
