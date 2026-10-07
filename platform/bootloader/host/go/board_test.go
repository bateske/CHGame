package main

// Which board: the Go tool against the shared vectors' board section, which
// the Python uploader writes (python -m chgame_upload.vectors --write ...).
// spec/chgame.md, "Devices and revisions"; platform/board/docs/protocol.md.

import (
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

type boardVectors struct {
	Board struct {
		Devices  map[string]uint32 `json:"devices"`
		Reserved map[string]uint32 `json:"reserved"`
		Names    []struct {
			Target uint32 `json:"target"`
			Name   string `json:"name"`
		} `json:"names"`
		Hello []struct {
			Payload  string `json:"payload"`
			Board    uint32 `json:"board"`
			Reported bool   `json:"reported"`
		} `json:"hello"`
		BootImage []struct {
			Name  string `json:"name"`
			Image string `json:"image"`
			Board uint32 `json:"board"`
		} `json:"boot_image"`
		Packs []struct {
			Device string `json:"device"`
			Header string `json:"header"`
		} `json:"packs"`
	} `json:"board"`
}

func TestBoards(t *testing.T) {
	data, err := os.ReadFile(filepath.Join("..", "..", "test", "protocol", "vectors.json"))
	if err != nil {
		t.Fatal(err)
	}
	var v boardVectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	b := v.Board
	if len(b.Devices) == 0 {
		t.Fatal("vectors.json has no board section (python -m chgame_upload.vectors --write ...)")
	}
	if len(b.Devices) != len(chgDevices) || len(b.Reserved) != len(chgReserved) {
		t.Errorf("devices %v reserved %v, want %v %v", chgDevices, chgReserved, b.Devices, b.Reserved)
	}
	for name, target := range b.Devices {
		if got, err := targetOf(name); err != nil || got != target {
			t.Errorf("device %s: 0x%08X %v, want 0x%08X", name, got, err, target)
		}
	}
	for name := range b.Reserved {
		if _, err := targetOf(name); err == nil {
			t.Errorf("%s is reserved: it must be refused", name)
		}
	}
	for _, n := range b.Names {
		if got := boardName(n.Target); got != n.Name {
			t.Errorf("name of 0x%08X: %q, want %q", n.Target, got, n.Name)
		}
	}
	for _, c := range b.Hello {
		h, err := parseHello(unhex(t, c.Payload))
		if err != nil {
			t.Fatal(err)
		}
		if h.Board != c.Board || h.BoardReported != c.Reported {
			t.Errorf("HELLO %s: board 0x%08X %v, want 0x%08X %v", c.Payload, h.Board, h.BoardReported, c.Board, c.Reported)
		}
	}
	for _, c := range b.BootImage {
		if got := bootImageBoard(unhex(t, c.Image)); got != c.Board {
			t.Errorf("boot image %s: board 0x%08X, want 0x%08X", c.Name, got, c.Board)
		}
	}
	for _, p := range b.Packs {
		target, err := targetOf(p.Device)
		if err != nil {
			t.Fatal(err)
		}
		pkg, err := chgPackFor(make([]byte, 64), "X", "", "", 0, target)
		if err != nil {
			t.Fatal(err)
		}
		if got := hex.EncodeToString(pkg[:chgHeaderBytes]); got != p.Header {
			t.Errorf("%s: header differs\n got %s\nwant %s", p.Device, got, p.Header)
		}
	}
}
