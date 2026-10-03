package main

// The Go tool against the shared vectors (test/protocol/vectors.json), which
// the Python uploader writes (python -m chgame_upload.vectors --write ...).
// The two implementations cannot drift apart without one of these failing.

import (
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

type vectorFile struct {
	Version string `json:"version"`
	CRC16   []struct {
		Data string `json:"data"`
		CRC  uint16 `json:"crc"`
	} `json:"crc16"`
	Frames []struct {
		Cmd     byte   `json:"cmd"`
		Payload string `json:"payload"`
		Frame   string `json:"frame"`
	} `json:"frames"`
	FrameTooBig struct {
		Cmd        byte `json:"cmd"`
		PayloadLen int  `json:"payload_len"`
	} `json:"frame_too_big"`
	Hello struct {
		Payload string `json:"payload"`
		Fields  struct {
			ProtoVersion byte   `json:"proto_version"`
			Mode         byte   `json:"mode"`
			AppState     byte   `json:"app_state"`
			BootVersion  uint16 `json:"boot_version"`
			AppStart     uint32 `json:"app_start"`
			AppMaxSize   uint32 `json:"app_max_size"`
			PageSize     uint16 `json:"page_size"`
			MaxPayload   uint16 `json:"max_payload"`
			UID          string `json:"uid"`
		} `json:"fields"`
		BadStatus struct {
			Payload string `json:"payload"`
			Status  byte   `json:"status"`
		} `json:"bad_status"`
		Short struct {
			Payload string `json:"payload"`
		} `json:"short"`
	} `json:"hello"`
	ChunkSize []struct {
		MaxPayload int `json:"max_payload"`
		Page       int `json:"page"`
		Chunk      int `json:"chunk"`
	} `json:"chunk_size"`
	PadToWord []struct {
		Len    int `json:"len"`
		Padded int `json:"padded"`
	} `json:"pad_to_word"`
	BootImage []struct {
		Name    string `json:"name"`
		Image   string `json:"image"`
		Verdict string `json:"verdict"`
	} `json:"boot_image"`
	Metadata struct {
		App  string `json:"app"`
		Page string `json:"page"`
	} `json:"metadata"`
	Image struct {
		Boot   string `json:"boot"`
		App    string `json:"app"`
		Length int    `json:"length"`
		SHA256 string `json:"sha256"`
	} `json:"image"`
	Layout map[string]int `json:"layout"`
}

func loadVectors(t *testing.T) *vectorFile {
	t.Helper()
	data, err := os.ReadFile(filepath.Join("..", "..", "test", "protocol", "vectors.json"))
	if err != nil {
		t.Fatalf("vectors.json: %v (write it with python -m chgame_upload.vectors --write ...)", err)
	}
	var v vectorFile
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	return &v
}

func unhex(t *testing.T, s string) []byte {
	t.Helper()
	b, err := hex.DecodeString(s)
	if err != nil {
		t.Fatal(err)
	}
	return b
}

func TestVersionMatchesPython(t *testing.T) {
	v := loadVectors(t)
	if v.Version != version {
		t.Fatalf("main.go says %s, the Python package %s", version, v.Version)
	}
}

func TestCRC16(t *testing.T) {
	v := loadVectors(t)
	for _, c := range v.CRC16 {
		if got := crc16(unhex(t, c.Data)); got != c.CRC {
			t.Errorf("crc16(%s) = 0x%04X, want 0x%04X", c.Data, got, c.CRC)
		}
	}
	if got := crc16([]byte("123456789")); got != 0x29B1 {
		t.Errorf("check value: 0x%04X", got)
	}
}

func TestBuildFrame(t *testing.T) {
	v := loadVectors(t)
	for _, f := range v.Frames {
		got, err := buildFrame(f.Cmd, unhex(t, f.Payload))
		if err != nil {
			t.Fatal(err)
		}
		if hex.EncodeToString(got) != f.Frame {
			t.Errorf("frame cmd 0x%02X: %x, want %s", f.Cmd, got, f.Frame)
		}
	}
	if _, err := buildFrame(v.FrameTooBig.Cmd, make([]byte, v.FrameTooBig.PayloadLen)); err == nil {
		t.Error("an oversize payload must be refused")
	}
}

func TestParseHello(t *testing.T) {
	v := loadVectors(t)
	h, err := parseHello(unhex(t, v.Hello.Payload))
	if err != nil {
		t.Fatal(err)
	}
	f := v.Hello.Fields
	if h.ProtoVersion != f.ProtoVersion || h.Mode != f.Mode || h.AppState != f.AppState ||
		h.BootVersion != f.BootVersion || h.AppStart != f.AppStart || h.AppMaxSize != f.AppMaxSize ||
		h.PageSize != f.PageSize || h.MaxPayload != f.MaxPayload || hex.EncodeToString(h.UID) != f.UID {
		t.Errorf("parsed %+v, want %+v", h, f)
	}
	if _, err := parseHello(unhex(t, v.Hello.BadStatus.Payload)); err == nil {
		t.Error("a non-OK HELLO must fail")
	} else if se, ok := err.(*StatusError); !ok || se.Status != v.Hello.BadStatus.Status {
		t.Errorf("want StatusError %d, got %v", v.Hello.BadStatus.Status, err)
	}
	if _, err := parseHello(unhex(t, v.Hello.Short.Payload)); err == nil {
		t.Error("a short HELLO must fail")
	}
}
