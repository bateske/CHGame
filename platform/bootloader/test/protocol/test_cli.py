"""The Python uploader's command line and its upload paths, without a board:
the Go-style flags platform.txt uses (its recipes, word for word), the
version pin against main.go, upload()/selfupdate()/flash_file() end to end
against a scripted bootloader behind a fake serial port, and the board checks
of burn, selfupdate and provision (wchisp scripted)."""
import io
import json
import pathlib
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
BOOT = HERE.parents[1]
sys.path.insert(0, str(BOOT / "host" / "py"))
import chgame_upload  # noqa: E402
from chgame_upload import chg as C, cli, client, layout as L, protocol as P, provision as W, upload as U  # noqa: E402

VECTORS = json.loads((HERE / "vectors.json").read_text(encoding="utf-8"))
PLATFORM_TXT = BOOT.parent / "board" / "arduino" / "CHGame" / "platform.txt"
BOARDS_TXT = PLATFORM_TXT.with_name("boards.txt")
CGR2 = 0x32524743           # a board reserved for the tests (none is at present)


def boot_image(target=0, n=3000):
    """A bootloader image for a board: linked for 0, its board word at 0x14."""
    img = bytearray(bytes(4) + struct.pack("<I", 0) + bytes((i * 7) & 0xFF for i in range(n)))
    struct.pack_into("<I", img, 0x14, target)
    return bytes(img)


class FakeSerial:
    """pyserial's Serial as the uploader uses it, with a CHGame bootloader
    behind it: every frame written is answered into the read buffer."""
    boot = None             # the FakeBoot every instance talks to (set by the test)

    def __init__(self, port, baudrate=115200, timeout=1.0, write_timeout=None):
        self.port, self.baudrate, self.timeout = port, baudrate, timeout
        self.dtr = True
        self.rx = bytearray()
        self.pending = bytearray()
        FakeSerial.boot.opened.append((port, baudrate))

    def reset_input_buffer(self):
        self.rx.clear()

    def write(self, data):
        self.pending += data
        while True:
            i = self.pending.find(P.SOF)
            if i < 0 or len(self.pending) < i + 8:
                return len(data)
            length = struct.unpack_from("<H", self.pending, i + 4)[0]
            end = i + 8 + length
            if len(self.pending) < end:
                return len(data)
            frame = bytes(self.pending[i:end])
            del self.pending[:end]
            cmd, payload = P.parse_frame(frame)
            self.rx += P.build_frame(cmd | P.RESPONSE_BIT, FakeSerial.boot.handle(cmd, payload))

    def flush(self):
        pass

    def read(self, n=1):
        out = bytes(self.rx[:n])
        del self.rx[:n]
        return out

    def close(self):
        pass


class FakeBoot:
    def __init__(self, boot_version=2, locked=False, board=None):
        self.flash = bytearray([L.ERASED]) * L.FLASH_SIZE
        self.boot_version, self.locked = boot_version, locked
        self.board = board              # None: a rev0 bootloader's HELLO, without the board field
        self.unlocked = False
        self.staged = None
        self.opened = []
        self.log = []

    def hello(self):
        return bytes([P.ST_OK, 1, P.MODE_BOOTLOADER, 0]) + struct.pack(
            "<HIIHH", self.boot_version, L.APP_START, L.APP_MAX_SIZE, L.PAGE_SIZE, 56) + bytes(12) + (
            b"" if self.board is None else struct.pack("<I", self.board))

    def handle(self, cmd, payload):
        self.log.append(cmd)
        if cmd == P.CMD_HELLO:
            return self.hello()
        if cmd == P.CMD_BEGIN:
            n, crc = struct.unpack("<II", payload)
            if n > L.APP_MAX_SIZE or n % 4:
                return bytes([0x04])
            self.flash[L.APP_START:L.META_ADDR + L.PAGE_SIZE] = bytes([L.ERASED]) * (L.APP_MAX_SIZE + L.PAGE_SIZE)
            self.staged = {"len": n, "crc": crc, "next": 0}
            return bytes([P.ST_OK])
        if cmd == P.CMD_WRITE:
            off = struct.unpack_from("<I", payload)[0]
            data = payload[4:]
            if not self.staged or off != self.staged["next"] or off + len(data) > self.staged["len"]:
                return bytes([0x02])
            self.flash[L.APP_START + off:L.APP_START + off + len(data)] = data
            self.staged["next"] += len(data)
            return bytes([P.ST_OK])
        if cmd == P.CMD_END:
            s = self.staged
            if not s or s["next"] != s["len"]:
                return bytes([0x02])
            app = bytes(self.flash[L.APP_START:L.APP_START + s["len"]])
            if zlib.crc32(app) & 0xFFFFFFFF != s["crc"]:
                return bytes([0x05])
            meta = struct.pack("<4I", L.META_MAGIC, L.META_VERSION, s["len"], s["crc"])
            self.flash[L.META_ADDR:L.META_ADDR + len(meta)] = meta
            self.staged = None
            return bytes([P.ST_OK])
        if cmd == P.CMD_READ:
            addr, n = struct.unpack("<IH", payload)
            return bytes([P.ST_OK]) + bytes(self.flash[addr:addr + n])
        if cmd in (P.CMD_RUN, P.CMD_STATUS, P.CMD_ABORT):
            return bytes([P.ST_OK])
        if cmd == P.CMD_DEV_UNLOCK:
            if self.locked:
                return bytes([0x07])
            self.unlocked = struct.unpack("<I", payload)[0] == U.DEV_KEY
            return bytes([P.ST_OK if self.unlocked else 0x07])
        if cmd == P.CMD_DEV_WRITE_BOOT:
            n, crc = struct.unpack("<II", payload)
            if not self.unlocked:
                return bytes([0x07])
            staged = bytes(self.flash[L.APP_START:L.APP_START + n])
            if zlib.crc32(staged) & 0xFFFFFFFF != crc:
                return bytes([0x05])
            self.flash[0:n] = staged
            return bytes([P.ST_OK])
        return bytes([0x01])


class Flags(unittest.TestCase):
    def test_go_spelling(self):
        self.assertEqual(cli.normalise(["-port", "COM3", "flash", "x.bin", "-run", "-verify"]),
                         ["--port", "COM3", "flash", "x.bin", "--run", "--verify"])
        self.assertEqual(cli.normalise(["--port", "-", "-5", "x-y"]), ["--port", "-", "-5", "x-y"])

    def test_duration(self):
        self.assertEqual(cli.duration("10"), 10.0)
        self.assertEqual(cli.duration("2.5"), 2.5)
        self.assertEqual(cli.duration("10s"), 10.0)
        self.assertEqual(cli.duration("500ms"), 0.5)
        self.assertEqual(cli.duration("1m"), 60.0)

    def test_platform_txt_says_so(self):
        """The board package's recipes are word for word the ones the vectors
        hold (both tools parse those below), and rev0 is the default board."""
        lines = PLATFORM_TXT.read_text(encoding="utf-8").splitlines()
        for key, pattern in VECTORS["platform_txt"]["recipes"].items():
            self.assertIn(f"{key}={pattern}", lines, f"platform.txt's {key}")
        self.assertIn(f"build.chgame_device={VECTORS['platform_txt']['default_device']}", lines)

    def test_boards_txt_names_devices(self):
        """Every board in boards.txt that names its device names one the tool
        knows, and rev1's board is rev1."""
        props = dict(ln.split("=", 1) for ln in BOARDS_TXT.read_text(encoding="utf-8").splitlines()
                     if "=" in ln and not ln.lstrip().startswith("#"))
        named = {k.split(".", 1)[0]: v for k, v in props.items() if k.endswith(".build.chgame_device")}
        self.assertEqual(named.get("rev1"), "rev1", "boards.txt: rev1.build.chgame_device=rev1")
        for board, dev in named.items():
            self.assertIn(dev, C.DEVICES, board)

    def test_platform_txt_recipes(self):
        """What Arduino makes of each recipe, as the vectors have it: the same
        verb, file and flags the Go tool reads (cli_test.go)."""
        for case in VECTORS["platform_txt"]["cases"]:
            with self.subTest(case["key"], argv=case["argv"]):
                a = cli.parse_args(case["argv"])
                got = {"cmd": a.cmd, "port": a.port or "", "verbose": a.verbose, "quiet": a.quiet,
                       "positional": [a.image] if hasattr(a, "image") else [], "run": getattr(a, "run", False),
                       "device": getattr(a, "device", None) or "", "method": getattr(a, "method", "usb"),
                       "wchisp": getattr(a, "wchisp", None) or "", "bootloader": getattr(a, "bootloader", None) or "",
                       "app": getattr(a, "app", None) or ""}
                self.assertEqual(got, case["want"])
        # the shapes before -device, as Arduino expands an older platform.txt
        a = cli.parse_args(["-verbose", "-port", "COM7", "flash", "build/CHFour.ino.bin", "-run"])
        self.assertEqual((a.cmd, a.port, a.image, a.run, a.verify, a.verbose), ("flash", "COM7", "build/CHFour.ino.bin", True, False, True))
        a = cli.parse_args(["-quiet", "-port", "COM7", "burn", "-method", "usb", "-wchisp", "W/wchisp.exe", "-bootloader", "B.bin"])
        self.assertEqual((a.cmd, a.method, a.wchisp, a.bootloader, a.app, a.quiet), ("burn", "usb", "W/wchisp.exe", "B.bin", None, True))
        a = cli.parse_args(["burn", "-method", "isp", "-wchisp", "W", "-bootloader", "B.bin", "-app", "A.bin"])
        self.assertEqual((a.method, a.app), ("isp", "A.bin"))
        a = cli.parse_args(["noop"])
        self.assertEqual(a.cmd, "noop")
        a = cli.parse_args(["-timeout", "500ms", "probe"])
        self.assertEqual(a.timeout, 0.5)
        a = cli.parse_args(["probe", "--port", "COM1"])
        self.assertEqual(a.port, "COM1")

    def test_pack(self):
        a = cli.parse_args(["-quiet", "pack", "build/CHFour.ino.bin"])
        self.assertEqual((a.cmd, a.image, a.out, a.title, a.quiet), ("pack", "build/CHFour.ino.bin", None, None, True))
        a = cli.parse_args(["pack", "x.bin", "-out", "X.CHG", "-title", "MY GAME", "-author", "ME", "-gameversion", "1.2"])
        self.assertEqual((a.out, a.title, a.author, a.gameversion), ("X.CHG", "MY GAME", "ME", "1.2"))
        with tempfile.TemporaryDirectory() as d:
            src = pathlib.Path(d) / "MyGame.ino.bin"
            src.write_bytes(bytes(range(256)) * 4)
            self.assertEqual(cli.main(["-quiet", "pack", str(src)]), 0)
            from chgame_upload import chg
            self.assertEqual((pathlib.Path(d) / "MyGame.ino.chg").read_bytes(), chg.pack(src.read_bytes(), "MYGAME"))

    def test_device_flags(self):
        """-device on every verb that writes, -yes on provision (burn takes it and never asks)."""
        a = cli.parse_args(["burn", "-method", "isp", "-bootloader", "B.bin", "-device", "rev1"])
        self.assertEqual((a.device, a.yes), ("rev1", False))
        a = cli.parse_args(["provision", "-bootloader", "B.bin", "-device", "rev1", "-yes"])
        self.assertEqual((a.cmd, a.device, a.yes), ("provision", "rev1", True))
        a = cli.parse_args(["provision", "-bootloader", "B.bin"])
        self.assertEqual((a.device, a.yes), (None, False))
        a = cli.parse_args(["selfupdate", "B.bin", "-device", "rev0"])
        self.assertEqual(a.device, "rev0")
        self.assertEqual(cli.parse_args(["pack", "x.bin"]).device, "rev0")

    def test_version_pinned_to_go(self):
        go = (BOOT / "host" / "go" / "main.go").read_text(encoding="utf-8")
        m = re.search(r'^\s*(?:const|var)?\s*version\s*=\s*"([^"]+)"', go, re.M)
        self.assertIsNotNone(m)
        self.assertEqual(chgame_upload.__version__, m.group(1))
        self.assertEqual(chgame_upload.__version__, "0.3.0")


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.boot = FakeBoot()
        FakeSerial.boot = self.boot
        self.patch = mock.patch.object(client.serial, "Serial", FakeSerial)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_upload_and_readback(self):
        image = bytes((i * 29 + 3) & 0xFF for i in range(5001))       # not a word multiple: padded
        with client.Client("FAKE", timeout=1.0) as c:
            r = U.upload(c, image, verify_readback=True)
        self.assertEqual(r["bytes"], 5004)
        self.assertTrue(r["readback_ok"])
        self.assertEqual(bytes(self.boot.flash[L.APP_START:L.APP_START + 5001]), image)
        self.assertEqual(self.boot.log[:3], [P.CMD_HELLO, P.CMD_BEGIN, P.CMD_WRITE])
        self.assertIn(P.CMD_END, self.boot.log)

    def test_too_big_is_refused_before_begin(self):
        with client.Client("FAKE", timeout=1.0) as c:
            with self.assertRaises(ValueError):
                U.upload(c, bytes(L.APP_MAX_SIZE + 4))
        self.assertNotIn(P.CMD_BEGIN, self.boot.log)

    def test_selfupdate(self):
        boot_img = bytes(4) + struct.pack("<I", 0) + bytes((i * 7) & 0xFF for i in range(3000))
        with client.Client("FAKE", timeout=1.0) as c:
            r = U.selfupdate(c, boot_img)
        self.assertTrue(r["promoted"])
        self.assertEqual(bytes(self.boot.flash[:len(boot_img)]), boot_img)
        self.assertLess(self.boot.log.index(P.CMD_DEV_UNLOCK), self.boot.log.index(P.CMD_BEGIN),
                        "the unlock must come before staging")

    def test_selfupdate_locked(self):
        self.boot.locked = True
        with client.Client("FAKE", timeout=1.0) as c:
            with self.assertRaises(RuntimeError) as cm:
                U.selfupdate(c, bytes(300))
        self.assertIn("locked", str(cm.exception))
        self.assertNotIn(P.CMD_BEGIN, self.boot.log)

    def test_flash_file(self):
        image = bytes((i * 11) & 0xFF for i in range(2048))
        with tempfile.TemporaryDirectory() as td:
            f = pathlib.Path(td) / "x.ino.bin"
            f.write_bytes(image)
            lines = []
            with mock.patch.object(client, "find_ports", return_value=["FAKE"]):
                r = U.flash_file(f, run=False, verify=True, log=lines.append)
        self.assertEqual(r["port"], "FAKE")
        self.assertTrue(r["readback_ok"])
        self.assertTrue(any(ln.startswith("readback: MATCHES") for ln in lines))
        self.assertEqual(bytes(self.boot.flash[L.APP_START:L.APP_START + 2048]), image)

    def test_flash_file_which_board(self):
        """flash -device refuses a board whose HELLO names another, before BEGIN."""
        self.boot.board = C.TARGET_REV1
        with tempfile.TemporaryDirectory() as td:
            f = pathlib.Path(td) / "x.ino.bin"
            f.write_bytes(bytes(1024))
            with mock.patch.object(client, "find_ports", return_value=["FAKE"]):
                with self.assertRaises(ValueError) as cm:
                    U.flash_file(f, run=False, device="rev0", log=None)
                self.assertIn("built for rev0 (CX35)", str(cm.exception))
                self.assertIn("rev1 (CGR1)", str(cm.exception))
                self.assertNotIn(P.CMD_BEGIN, self.boot.log)
                U.flash_file(f, run=False, device="rev1", log=None)
        self.assertIn(P.CMD_END, self.boot.log)

    def test_burn_refuses_another_boards_bootloader(self):
        """burn (usb and isp) and selfupdate with -device: an image whose board
        word names another board is refused before any port or wchisp is used."""
        with tempfile.TemporaryDirectory() as td:
            b = pathlib.Path(td) / "boot.bin"
            b.write_bytes(boot_image(C.TARGET_REV1))
            for argv in (["burn", "-method", "usb", "-bootloader", str(b), "-device", "rev0"],
                         ["burn", "-method", "isp", "-wchisp", "W", "-bootloader", str(b), "-device", "rev0"],
                         ["provision", "-wchisp", "W", "-bootloader", str(b), "-device", "rev0", "-yes"],
                         ["selfupdate", str(b), "-device", "rev0", "-yes"]):
                with self.subTest(argv=argv), mock.patch.object(subprocess, "run") as run, \
                        mock.patch.object(client, "find_ports", return_value=["FAKE"]):
                    with self.assertRaises(SystemExit) as cm:
                        cli.main(argv)
                    self.assertIn("built for rev1 (CGR1), not rev0 (CX35)", str(cm.exception.code))
                    run.assert_not_called()
                    self.assertEqual(self.boot.opened, [])
            b.write_bytes(boot_image(0))                # a rev0 image (word 0) is not rev1's either
            with self.assertRaises(SystemExit) as cm:
                cli.main(["burn", "-method", "usb", "-bootloader", str(b), "-device", "rev1"])
            self.assertIn("built for rev0 (CX35), not rev1 (CGR1)", str(cm.exception.code))
            with self.assertRaises(SystemExit) as cm:   # a device the tool does not know
                cli.main(["burn", "-method", "usb", "-bootloader", str(b), "-device", "rev9"])
            self.assertIn("known: rev0, rev1", str(cm.exception.code))
            self.assertEqual(self.boot.opened, [])


class FakeWchisp:
    """subprocess.run as provision() calls wchisp: probe, info, erase, flash."""
    def __init__(self, devices=1, uid="CD-AB-88-D8-60-BE-B5-42"):
        self.devices, self.uid, self.calls = devices, uid, []

    def __call__(self, args, **kw):
        verb = args[1]
        self.calls.append(verb)
        out = {"probe": f"Found {self.devices} USB devices\n" + "".join(
                   f"Device #{i}: CH32X035G8U6[0x5623]\n" for i in range(self.devices)),
               "info": "Chip: CH32X035G8U6[0x5623]\n" + (f"Chip UID: {self.uid}\n" if self.uid else ""),
               "erase": "Erased\n", "flash": "Verify OK\n"}[verb]
        return subprocess.CompletedProcess(args, 0, out, "")


class Provision(unittest.TestCase):
    """The factory ISP path with wchisp scripted: one device or none, the chip
    and the image's board shown, a question before erasing unless -yes, and
    burn -method isp (Arduino's) never asking."""

    def run_cli(self, argv, wchisp, answer=None):
        def ask(prompt):
            if answer is None:
                raise AssertionError("must not ask")
            if isinstance(answer, BaseException):
                raise answer
            return answer
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as td:
            b = pathlib.Path(td) / "boot.bin"
            b.write_bytes(boot_image(C.TARGET_REV1))
            tool = pathlib.Path(td) / "wchisp.exe"
            tool.write_bytes(b"")
            argv = [str(b) if x == "BOOT" else str(tool) if x == "WCHISP" else x for x in argv]
            with mock.patch.object(subprocess, "run", wchisp), mock.patch("builtins.input", ask), redirect_stdout(out):
                try:
                    code = cli.main(argv)
                except SystemExit as e:
                    code = e.code
        return code, out.getvalue()

    def test_asks_then_writes(self):
        w = FakeWchisp()
        code, out = self.run_cli(["provision", "-wchisp", "WCHISP", "-bootloader", "BOOT", "-device", "rev1"], w,
                                 answer="y")
        self.assertEqual(code, 0)
        self.assertEqual(w.calls, ["probe", "info", "erase", "flash"])
        self.assertIn("chip UID    : CD-AB-88-D8-60-BE-B5-42", out)
        self.assertIn("for rev1 (CGR1)", out)

    def test_no_answer_erases_nothing(self):
        for answer in ("n", "", EOFError()):
            w = FakeWchisp()
            code, out = self.run_cli(["provision", "-wchisp", "WCHISP", "-bootloader", "BOOT"], w, answer=answer)
            self.assertIn("not confirmed: nothing was erased", str(code))
            self.assertEqual(w.calls, ["probe", "info"])

    def test_yes_and_burn_do_not_ask(self):
        for argv in (["provision", "-yes", "-wchisp", "WCHISP", "-bootloader", "BOOT", "-device", "rev1"],
                     ["-quiet", "burn", "-method", "isp", "-device", "rev1", "-wchisp", "WCHISP", "-bootloader", "BOOT"]):
            w = FakeWchisp(uid=None)
            code, out = self.run_cli(argv, w)
            self.assertEqual(code, 0, argv)
            self.assertEqual(w.calls, ["probe", "info", "erase", "flash"])
            self.assertIn("chip UID    : not reported by wchisp", out)

    def test_several_or_no_devices(self):
        for n, says in ((2, "finds 2 devices in factory ISP mode"), (0, "no device is in factory ISP mode")):
            w = FakeWchisp(devices=n)
            code, _ = self.run_cli(["provision", "-yes", "-wchisp", "WCHISP", "-bootloader", "BOOT"], w)
            self.assertIn(says, str(code))
            self.assertEqual(w.calls, ["probe"])

    def test_reserved_device(self):
        with mock.patch.dict(C.RESERVED, {"rev2": CGR2}):
            w = FakeWchisp()
            code, _ = self.run_cli(["provision", "-yes", "-wchisp", "WCHISP", "-bootloader", "BOOT", "-device", "rev2"], w)
            self.assertIn("rev2 is reserved for a board that is not defined yet", str(code))
            self.assertEqual(w.calls, [])


if __name__ == "__main__":
    unittest.main()
