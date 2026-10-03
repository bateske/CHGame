# The format of a game's README

Every game (`platform/board/arduino/CHGame/libraries/CHGame/examples/Games/`) has the same README: short, in the same order, with
one picture. A reader should know in a minute what the game is, how to play
it, and what its code shows about the platform. Everything for someone
*changing* the game goes in its `NOTES.md` instead.
[platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHFour/README.md](../platform/board/arduino/CHGame/libraries/CHGame/examples/Games/CHFour/README.md) is the model.

```markdown
# CHName: Subtitle        (or just # CHName)

One or two sentences: what you do in the game, and its theme.

![CHName gameplay](docs/gameplay.gif)

## Controls

| Button | Action |
|---|---|
| ... | ... |

## Rules

The rules of the game itself, briefly: a short paragraph, a list or a table.

## How to play

The modes, opponents, stakes and options, and how a session goes.
One line on getting it onto the handheld.

## Developer notes

- Three to six bullets: what is interesting here as an example of the
  CHGame library, each naming the file to read.

## Credits

Exactly as the game's NOTICE gives them.
```

## The parts

- **Title.** `# CHName: Subtitle`, with a colon, when the game's name on its
  own title screen says more than the folder name does
  (`# CHFour: Four in a Row`). When it would only repeat it, the title is
  the name alone (`# CHChess`, not `# CHChess: Chess`).
- **Hook.** One or two sentences, no more. The play first, then the theme.
- **The picture.** One GIF, `docs/gameplay.gif`, no more than 1 MB: the
  title screen, then several short clips of play. No other GIF, no table
  of GIFs, no screenshots. `tools/scripts/gameplay.txt` records the clips
  (`01_title`, `02_...`) and `chgame gif` joins them
  and checks the size; `--check` checks every game's.
- **Controls.** One table, a row per button or gesture. START held for
  three seconds is the platform's exit to the menu: not listed.
- **Rules.** What a player who has never met the game needs. Paytables and
  scoring tables belong here.
- **How to play.** Modes, opponents, stakes, options, what is saved. It
  ends with the same line in every game: the Arduino IDE route (*File >
  Examples*, *Tools > USB* **Upload only**), `chgame upload` from a clone,
  and the release's SD card zip. Its link to *Installing* is absolute
  (`https://github.com/bateske/CHGame#installing`): the README is also read
  inside the installed board package, where the repository is not.
- **Developer notes.** A short list for someone reading the game as an
  example sketch: which library module it shows off, a technique worth
  copying, where the size or speed was won. Sizes, test instructions,
  script commands and open items live in `NOTES.md`; the list ends with a
  link to it.
- **Credits.** Last. The same names, works and licences as `NOTICE`.

No banner, no installing section, no development section, no sizes that
go stale. Plain hyphens, LF line endings.
