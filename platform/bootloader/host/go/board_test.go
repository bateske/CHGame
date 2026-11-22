package main

// Which board: the Go tool against the shared vectors' board section, which
// the Python uploader writes (python -m chgame_upload.vectors --write ...).
// spec/chgame.md, "Devices and revisions"; platform/board/docs/protocol.md.

import (
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type boardVectors struct {
	Board struct {
		Devices  map[string]uint32 `json:"devices"`
		Reserved map[string]uint32 `json:"reserved"`
		Known    string            `json:"known"`
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
		DeviceCheck []struct {
			Image  string `json:"image"`
			Device string `json:"device"`
			OK     bool   `json:"ok"`
		} `json:"device_check"`
		ReservedExample struct {
			Device string `json:"device"`
			Target uint32 `json:"target"`
			Name   string `json:"name"`
		} `json:"reserved_example"`
		Packs []struct {
			Device string `json:"device"`
			Header string `json:"header"`
		} `json:"packs"`
	} `json:"board"`
	Wchisp struct {
		Probe []struct {
			Output  string   `json:"output"`
			Devices []string `json:"devices"`
		} `json:"probe"`
		Info []struct {
			Output string `json:"output"`
			UID    string `json:"uid"`
		} `json:"info"`
	} `json:"wchisp"`
}

func loadBoardVectors(t *testing.T) *boardVectors {
	t.Helper()
	data, err := os.ReadFile(filepath.Join("..", "..", "test", "protocol", "vectors.json"))
	if err != nil {
		t.Fatal(err)
	}
	var v boardVectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	if len(v.Board.Devices) == 0 {
		t.Fatal("vectors.json has no board section (python -m chgame_upload.vectors --write ...)")
	}
	return &v
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
	images := map[string][]byte{}
	for _, c := range b.BootImage {
		images[c.Name] = unhex(t, c.Image)
		if got := bootImageBoard(images[c.Name]); got != c.Board {
			t.Errorf("boot image %s: board 0x%08X, want 0x%08X", c.Name, got, c.Board)
		}
	}
	if got := knownDevices(); got != b.Known {
		t.Errorf("known devices %q, want %q", got, b.Known)
	}
	if _, err := targetOf("rev9"); err == nil || !strings.Contains(err.Error(), "(known: "+b.Known+")") {
		t.Errorf("an unknown device: %v", err)
	}
	for _, c := range b.DeviceCheck {
		err := checkBootBoard(images[c.Image], c.Device)
		if (err == nil) != c.OK {
			t.Errorf("image %s, -device %q: %v, want ok=%v", c.Image, c.Device, err, c.OK)
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

// TestReservedBoard: no board is reserved now (rev1 was until it was
// defined), so one is patched in to check it is refused by name wherever a
// device is taken, as the Python tool refuses it.
func TestReservedBoard(t *testing.T) {
	r := loadBoardVectors(t).Board.ReservedExample
	if _, known := chgDevices[r.Device]; known || r.Device == "" {
		t.Fatalf("the example %q must be a board neither table holds", r.Device)
	}
	chgReserved[r.Device] = r.Target
	defer delete(chgReserved, r.Device)
	if got := boardName(r.Target); got != r.Name {
		t.Errorf("name %q, want %q", got, r.Name)
	}
	if _, err := targetOf(r.Device); err == nil || !strings.Contains(err.Error(), "reserved for a board that is not defined yet") {
		t.Errorf("targetOf(%s): %v", r.Device, err)
	}
	if err := checkBootBoard(make([]byte, 256), r.Device); err == nil || !strings.Contains(err.Error(), "reserved") {
		t.Errorf("checkBootBoard(-device %s): %v", r.Device, err)
	}
}

// TestWchispOutput: what provision reads from wchisp, as the Python tool reads it.
func TestWchispOutput(t *testing.T) {
	v := loadBoardVectors(t)
	if len(v.Wchisp.Probe) == 0 || len(v.Wchisp.Info) == 0 {
		t.Fatal("vectors.json has no wchisp section (python -m chgame_upload.vectors --write ...)")
	}
	for _, c := range v.Wchisp.Probe {
		got := wchispDevices(c.Output)
		if strings.Join(got, "|") != strings.Join(c.Devices, "|") {
			t.Errorf("probe %q: %q, want %q", c.Output, got, c.Devices)
		}
	}
	for _, c := range v.Wchisp.Info {
		if got := wchispUID(c.Output); got != c.UID {
			t.Errorf("info %q: %q, want %q", c.Output, got, c.UID)
		}
	}
}
