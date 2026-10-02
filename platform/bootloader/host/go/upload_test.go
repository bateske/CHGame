package main

import (
	"crypto/sha256"
	"encoding/hex"
	"strings"
	"testing"
)

func TestChunkSizeAndPadding(t *testing.T) {
	v := loadVectors(t)
	for _, c := range v.ChunkSize {
		if got := chunkSize(c.MaxPayload, c.Page); got != c.Chunk {
			t.Errorf("chunkSize(%d, %d) = %d, want %d", c.MaxPayload, c.Page, got, c.Chunk)
		}
	}
	for _, p := range v.PadToWord {
		if got := len(padToWord(make([]byte, p.Len))); got != p.Padded {
			t.Errorf("padToWord(%d) -> %d, want %d", p.Len, got, p.Padded)
		}
	}
}

func verdict(err error) string {
	switch {
	case err == nil:
		return "ok"
	case strings.Contains(err.Error(), "too small"):
		return "small"
	case strings.Contains(err.Error(), "over the"):
		return "big"
	case strings.Contains(err.Error(), "is a sketch"):
		return "sketch"
	}
	return "other"
}

func TestCheckBootImage(t *testing.T) {
	v := loadVectors(t)
	for _, b := range v.BootImage {
		if got := verdict(checkBootImage(unhex(t, b.Image))); got != b.Verdict {
			t.Errorf("%s: %s, want %s", b.Name, got, b.Verdict)
		}
	}
}

func TestMetadataAndImage(t *testing.T) {
	v := loadVectors(t)
	if got := hex.EncodeToString(buildMetadata(unhex(t, v.Metadata.App))); got != v.Metadata.Page {
		t.Errorf("metadata page differs:\n%s\n%s", got, v.Metadata.Page)
	}
	img, err := buildImage(unhex(t, v.Image.Boot), unhex(t, v.Image.App))
	if err != nil {
		t.Fatal(err)
	}
	if len(img) != v.Image.Length {
		t.Errorf("image length %d, want %d", len(img), v.Image.Length)
	}
	sum := sha256.Sum256(img)
	if hex.EncodeToString(sum[:]) != v.Image.SHA256 {
		t.Errorf("image sha256 %x, want %s", sum, v.Image.SHA256)
	}
}

func TestLayout(t *testing.T) {
	v := loadVectors(t)
	want := map[string]int{
		"CHGAME_FLASH_SIZE": flashSize, "CHGAME_PAGE_SIZE": pageSize, "CHGAME_BOOT_SIZE": bootSize,
		"CHGAME_APP_START": appStart, "CHGAME_META_ADDR": metaAddr, "CHGAME_APP_MAX_SIZE": appMaxSize,
		"CHGAME_META_MAGIC": metaMagic, "CHGAME_META_VERSION": metaVersion,
	}
	for k, val := range want {
		if v.Layout[k] != val {
			t.Errorf("%s: Go has 0x%X, the layout says 0x%X", k, val, v.Layout[k])
		}
	}
	if devKey != 0x43484744 {
		t.Errorf("devKey")
	}
}
