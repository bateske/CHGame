package main

// pack against the shared vectors: the same package bytes, refusals, default
// names and titles as the Python tool (and tools/chgpack.py, which the Python
// tests compare with).

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

type chgVectors struct {
	Chg struct {
		App   string `json:"app"`
		Packs []struct {
			Title      string `json:"title"`
			Author     string `json:"author"`
			Version    string `json:"version"`
			AppVersion uint32 `json:"app_version"`
			Header     string `json:"header"`
			Length     int    `json:"length"`
			SHA256     string `json:"sha256"`
		} `json:"packs"`
		Refused []struct {
			Name   string `json:"name"`
			Length int    `json:"length"`
			Image  string `json:"image"`
		} `json:"refused"`
		MaxOKLength int `json:"max_ok_length"`
		Names       []struct {
			Path  string `json:"path"`
			Title string `json:"title"`
			Out   string `json:"out"`
		} `json:"names"`
	} `json:"chg"`
}

func TestChgPack(t *testing.T) {
	data, err := os.ReadFile(filepath.Join("..", "..", "test", "protocol", "vectors.json"))
	if err != nil {
		t.Fatal(err)
	}
	var v chgVectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	if len(v.Chg.Packs) == 0 {
		t.Fatal("vectors.json has no chg section (python -m chgame_upload.vectors --write ...)")
	}
	app := unhex(t, v.Chg.App)
	for _, p := range v.Chg.Packs {
		pkg, err := chgPack(app, p.Title, p.Author, p.Version, p.AppVersion)
		if err != nil {
			t.Fatalf("%s: %v", p.Title, err)
		}
		if got := hex.EncodeToString(pkg[:chgHeaderBytes]); got != p.Header {
			t.Errorf("%s: header differs\n got %s\nwant %s", p.Title, got, p.Header)
		}
		sum := sha256.Sum256(pkg)
		if len(pkg) != p.Length || hex.EncodeToString(sum[:]) != p.SHA256 {
			t.Errorf("%s: %d B %x, want %d B %s", p.Title, len(pkg), sum, p.Length, p.SHA256)
		}
	}
	for _, r := range v.Chg.Refused {
		img := make([]byte, r.Length)
		if r.Image != "" {
			img = unhex(t, r.Image)
		}
		if _, err := chgPack(img, "X", "", "", 0); err == nil {
			t.Errorf("%s: must be refused", r.Name)
		}
	}
	if _, err := chgPack(make([]byte, v.Chg.MaxOKLength), "X", "", "", 0); err != nil {
		t.Errorf("the largest image must be accepted: %v", err)
	}
	for _, n := range v.Chg.Names {
		if got := chgDefaultTitle(n.Path); got != n.Title {
			t.Errorf("title of %s: %q, want %q", n.Path, got, n.Title)
		}
		if got := filepath.ToSlash(chgDefaultOutput(filepath.FromSlash(n.Path))); got != n.Out {
			t.Errorf("output of %s: %q, want %q", n.Path, got, n.Out)
		}
	}
}
