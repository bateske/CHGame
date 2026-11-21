package main

// The command line: what this tool makes of the board package's recipes
// (platform.txt, word for word as the shared vectors hold them; the Python
// tool's test_cli.py parses the same command lines), and flags on either
// side of the verb.

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"
)

type recipeVectors struct {
	PlatformTxt struct {
		Recipes       map[string]string `json:"recipes"`
		DefaultDevice string            `json:"default_device"`
		Cases         []struct {
			Key  string   `json:"key"`
			Argv []string `json:"argv"`
			Want struct {
				Cmd        string   `json:"cmd"`
				Port       string   `json:"port"`
				Verbose    bool     `json:"verbose"`
				Quiet      bool     `json:"quiet"`
				Positional []string `json:"positional"`
				Run        bool     `json:"run"`
				Device     string   `json:"device"`
				Method     string   `json:"method"`
				Wchisp     string   `json:"wchisp"`
				Bootloader string   `json:"bootloader"`
				App        string   `json:"app"`
			} `json:"want"`
		} `json:"cases"`
	} `json:"platform_txt"`
}

func loadRecipeVectors(t *testing.T) *recipeVectors {
	t.Helper()
	data, err := os.ReadFile(filepath.Join("..", "..", "test", "protocol", "vectors.json"))
	if err != nil {
		t.Fatal(err)
	}
	var v recipeVectors
	if err := json.Unmarshal(data, &v); err != nil {
		t.Fatal(err)
	}
	if len(v.PlatformTxt.Cases) == 0 {
		t.Fatal("vectors.json has no platform_txt section (python -m chgame_upload.vectors --write ...)")
	}
	return &v
}

// TestPlatformTxtRecipes: each command line Arduino makes of a recipe gives
// the verb, file and flags the vectors say.
func TestPlatformTxtRecipes(t *testing.T) {
	for _, c := range loadRecipeVectors(t).PlatformTxt.Cases {
		inv, err := parseCommand(c.Argv, io.Discard)
		if err != nil {
			t.Fatalf("%s %q: %v", c.Key, c.Argv, err)
		}
		positional := inv.positional
		if positional == nil {
			positional = []string{}
		}
		got := []any{inv.cmd, inv.o.port, inv.o.verbose, inv.o.quiet, positional, inv.run, inv.device,
			inv.method, inv.wchispPath, inv.bootFile, inv.appFile}
		w := c.Want
		if w.Positional == nil {
			w.Positional = []string{}
		}
		want := []any{w.Cmd, w.Port, w.Verbose, w.Quiet, w.Positional, w.Run, w.Device,
			w.Method, w.Wchisp, w.Bootloader, w.App}
		if !reflect.DeepEqual(got, want) {
			t.Errorf("%s %q:\n got %v\nwant %v", c.Key, c.Argv, got, want)
		}
	}
}

// TestPlatformTxtSaysSo: the board package's recipes are word for word the
// ones the vectors hold, and rev0 is its default board.
func TestPlatformTxtSaysSo(t *testing.T) {
	v := loadRecipeVectors(t).PlatformTxt
	data, err := os.ReadFile(filepath.Join("..", "..", "..", "board", "arduino", "CHGame", "platform.txt"))
	if err != nil {
		t.Skipf("not in the CHGame repository: %v", err)
	}
	lines := map[string]bool{}
	for _, ln := range strings.Split(strings.ReplaceAll(string(data), "\r\n", "\n"), "\n") {
		lines[ln] = true
	}
	for key, pattern := range v.Recipes {
		if !lines[key+"="+pattern] {
			t.Errorf("platform.txt does not say\n%s=%s", key, pattern)
		}
	}
	if !lines["build.chgame_device="+v.DefaultDevice] {
		t.Errorf("platform.txt does not say build.chgame_device=%s", v.DefaultDevice)
	}
}

// TestFlagsBeforeTheVerb: the common flags keep their values whichever side
// of the verb they are on. Before 0.3.0, binding the verb's flags reset them,
// so platform.txt's `-port "{serial.port}" flash ...` lost the port.
func TestFlagsBeforeTheVerb(t *testing.T) {
	for _, argv := range [][]string{
		{"-port", "COM7", "-timeout", "3s", "-verbose", "info"},
		{"info", "-port", "COM7", "-timeout", "3s", "-verbose"},
		{"-port", "COM7", "info", "-timeout", "3s", "-verbose"},
	} {
		inv, err := parseCommand(argv, io.Discard)
		if err != nil {
			t.Fatal(err)
		}
		if inv.o.port != "COM7" || inv.o.timeout != 3*time.Second || !inv.o.verbose || inv.o.quiet {
			t.Errorf("%q: port %q timeout %v verbose %v quiet %v", argv, inv.o.port, inv.o.timeout, inv.o.verbose, inv.o.quiet)
		}
	}
	inv, err := parseCommand([]string{"probe"}, io.Discard)
	if err != nil || inv.o.timeout != 10*time.Second || inv.o.port != "" {
		t.Errorf("defaults: %+v %v", inv.o, err)
	}
	inv, err = parseCommand([]string{"provision", "-bootloader", "B.bin", "-device", "rev1", "-yes"}, io.Discard)
	if err != nil || inv.bootFile != "B.bin" || inv.device != "rev1" || !inv.yes {
		t.Errorf("provision: %+v %v", inv, err)
	}
	if _, err := parseCommand(nil, io.Discard); err != errNoCommand {
		t.Errorf("no verb: %v", err)
	}
	if _, err := parseCommand([]string{"flash", "-nosuchflag"}, io.Discard); err == nil {
		t.Error("an unknown flag must be refused")
	}
}
