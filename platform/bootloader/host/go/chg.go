package main

// CHG packages for the SD game menu: `chgame-upload pack`.
//
// A package is a 512-byte header plus the program image as flash would write
// it (docs/chg-format.md in the CHGame repository). platform.txt runs pack
// after every build, so Sketch > Export Compiled Binary leaves a .chg beside
// the .bin: copy it into the card's GAMES folder and the menu lists it.
//
// The constants mirror platform/bootloader/shared/chg_format.h; the shared
// vectors (test/protocol/vectors.json) hold this, the Python tool and
// tools/chgpack.py to the same bytes.

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
	"path/filepath"
	"strings"
)

const (
	chgMagic         = 0x31474843 // "CHG1"
	chgFormatVersion = 1
	chgHeaderBytes   = 512
	chgTargetID      = 0x35335843 // "CX35": CHGame, CH32X035G8U6
	chgLayoutID      = 0x003000F7 // app at 0x3000, metadata page at 0xF700
	chgBootSig       = 0x4C424843 // "CHBL" at payload offset 8 marks a bootloader image
	chgTitleLen      = 32
	chgAuthorLen     = 16
	chgVerstrLen     = 8
)

func chgText(dst []byte, s, what string) error {
	if len(s) >= len(dst) {
		return fmt.Errorf("%s must be printable ASCII, at most %d characters", what, len(dst)-1)
	}
	for i := 0; i < len(s); i++ {
		if s[i] < 32 || s[i] > 126 {
			return fmt.Errorf("%s must be printable ASCII, at most %d characters", what, len(dst)-1)
		}
	}
	copy(dst, s)
	return nil
}

// chgDefaultTitle: MyGame.ino.bin -> MYGAME, the sketch's name as the menu's capitals.
func chgDefaultTitle(path string) string {
	base := filepath.Base(path)
	if i := strings.Index(base, "."); i >= 0 {
		base = base[:i]
	}
	t := strings.ToUpper(base)
	if len(t) > chgTitleLen-1 {
		t = t[:chgTitleLen-1]
	}
	if t == "" {
		t = "PROGRAM"
	}
	return t
}

// chgDefaultOutput: MyGame.ino.bin -> MyGame.ino.chg, beside it (Export
// Compiled Binary copies every <project>.* file from the build folder).
func chgDefaultOutput(path string) string {
	ext := filepath.Ext(path)
	if strings.EqualFold(ext, ".bin") {
		return path[:len(path)-len(ext)] + ".chg"
	}
	return path + ".chg"
}

func chgPack(image []byte, title, author, ver string, appVersion uint32) ([]byte, error) {
	payload := padToWord(image)
	if len(payload) == 0 || len(payload) > appMaxSize {
		return nil, fmt.Errorf("image is %d B; the limit is %d B", len(payload), appMaxSize)
	}
	if len(payload) >= 12 && binary.LittleEndian.Uint32(payload[8:]) == chgBootSig {
		return nil, fmt.Errorf("this is a bootloader image, not a program")
	}
	h := make([]byte, chgHeaderBytes)
	le := binary.LittleEndian
	le.PutUint32(h[0x00:], chgMagic)
	le.PutUint16(h[0x04:], chgFormatVersion)
	le.PutUint16(h[0x06:], chgHeaderBytes)
	le.PutUint32(h[0x08:], chgTargetID)
	le.PutUint32(h[0x0C:], chgLayoutID)
	le.PutUint32(h[0x10:], uint32(len(payload)))
	le.PutUint32(h[0x14:], crc32.ChecksumIEEE(payload))
	le.PutUint32(h[0x18:], appVersion)
	if err := chgText(h[0x20:0x20+chgTitleLen], title, "title"); err != nil {
		return nil, err
	}
	if err := chgText(h[0x40:0x40+chgAuthorLen], author, "author"); err != nil {
		return nil, err
	}
	if err := chgText(h[0x50:0x50+chgVerstrLen], ver, "version"); err != nil {
		return nil, err
	}
	le.PutUint32(h[0x1FC:], crc32.ChecksumIEEE(h[:0x1FC]))
	return append(h, payload...), nil
}
