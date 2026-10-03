"""The Python uploader's command line and its upload paths, without a board:
the Go-style flags platform.txt uses, the version pin against main.go, and
upload()/selfupdate()/flash_file() end to end against a scripted bootloader
behind a fake serial port."""
import pathlib
import re
import struct
import sys
import tempfile
import unittest
import zlib
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
BOOT = HERE.parents[1]
sys.path.insert(0, str(BOOT / "host" / "py"))
import chgame_upload  # noqa: E402
from chgame_upload import cli, client, layout as L, protocol as P, upload as U  # noqa: E402


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
    def __init__(self, boot_version=2, locked=False):
        self.flash = bytearray([L.ERASED]) * L.FLASH_SIZE
        self.boot_version, self.locked = boot_version, locked
        self.unlocked = False
        self.staged = None
        self.opened = []
        self.log = []

    def hello(self):
        return bytes([P.ST_OK, 1, P.MODE_BOOTLOADER, 0]) + struct.pack(
            "<HIIHH", self.boot_version, L.APP_START, L.APP_MAX_SIZE, L.PAGE_SIZE, 56) + bytes(12)

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

    def test_platform_txt_recipes(self):
        # tools.chgame_upload.upload.pattern / bootloader.pattern / program.pattern, as Arduino expands them
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

    def test_version_pinned_to_go(self):
        go = (BOOT / "host" / "go" / "main.go").read_text(encoding="utf-8")
        m = re.search(r'^\s*(?:const|var)?\s*version\s*=\s*"([^"]+)"', go, re.M)
        self.assertIsNotNone(m)
        self.assertEqual(chgame_upload.__version__, m.group(1))


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


if __name__ == "__main__":
    unittest.main()
