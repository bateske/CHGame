"""The Python uploader against the shared vectors (vectors.json), and the
vectors file against what the package computes now.

    python -m unittest discover -s platform/bootloader/test/protocol -v
"""
import hashlib
import json
import pathlib
import re
import struct
import sys
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "host" / "py"))
from chgame_upload import chg as C, image as I, layout as L, protocol as P, upload as U, vectors as V  # noqa: E402
from chgame_upload import provision as W  # noqa: E402

VECTORS = json.loads((HERE / "vectors.json").read_text(encoding="utf-8"))


class Vectors(unittest.TestCase):
    def test_file_is_current(self):
        self.assertEqual(json.loads(json.dumps(V.generate())), VECTORS,
                         "vectors.json is stale: python -m chgame_upload.vectors --write platform/bootloader/test/protocol/vectors.json")

    def test_crc16(self):
        for c in VECTORS["crc16"]:
            self.assertEqual(P.crc16(bytes.fromhex(c["data"])), c["crc"])
        self.assertEqual(P.crc16(b"123456789"), 0x29B1)          # CRC-16/CCITT-FALSE's check value

    def test_frames(self):
        for f in VECTORS["frames"]:
            frame = bytes.fromhex(f["frame"])
            self.assertEqual(P.build_frame(f["cmd"], bytes.fromhex(f["payload"])), frame)
            cmd, payload = P.parse_frame(frame)
            self.assertEqual((cmd, payload), (f["cmd"], bytes.fromhex(f["payload"])))
        with self.assertRaises(ValueError):
            P.build_frame(VECTORS["frame_too_big"]["cmd"], bytes(VECTORS["frame_too_big"]["payload_len"]))

    def test_hello(self):
        h = VECTORS["hello"]
        parsed = P.Hello.parse(bytes.fromhex(h["payload"]))
        for k, v in h["fields"].items():
            got = getattr(parsed, k)
            self.assertEqual(got.hex() if isinstance(got, bytes) else got, v, k)
        with self.assertRaises(P.StatusError) as cm:
            P.Hello.parse(bytes.fromhex(h["bad_status"]["payload"]))
        self.assertEqual(cm.exception.status, h["bad_status"]["status"])
        with self.assertRaises(P.ProtocolError):
            P.Hello.parse(bytes.fromhex(h["short"]["payload"]))

    def test_chunk_and_pad(self):
        for c in VECTORS["chunk_size"]:
            self.assertEqual(U.chunk_size(c["max_payload"], c["page"]), c["chunk"])
        for p in VECTORS["pad_to_word"]:
            self.assertEqual(len(U.pad_to_word(bytes(p["len"]))), p["padded"])
            self.assertEqual(len(I.pad_to_word(bytes(p["len"]))), p["padded"])

    def test_boot_image(self):
        for b in VECTORS["boot_image"]:
            self.assertEqual(V._verdict(bytes.fromhex(b["image"])), b["verdict"], b["name"])

    def test_metadata_and_image(self):
        m = VECTORS["metadata"]
        self.assertEqual(I.build_metadata(bytes.fromhex(m["app"])).hex(), m["page"])
        im = VECTORS["image"]
        img = I.trim(I.build_image(bytes.fromhex(im["boot"]), bytes.fromhex(im["app"])))
        self.assertEqual(len(img), im["length"])
        self.assertEqual(hashlib.sha256(img).hexdigest(), im["sha256"])

    def test_layout(self):
        self.assertEqual(L.as_dict(), VECTORS["layout"])

    def test_chg(self):
        v = VECTORS["chg"]
        app = bytes.fromhex(v["app"])
        for p in v["packs"]:
            pkg = C.pack(app, p["title"], p["author"], p["version"], p["app_version"])
            self.assertEqual(pkg[:C.HEADER_BYTES].hex(), p["header"], p["title"])
            self.assertEqual((len(pkg), hashlib.sha256(pkg).hexdigest()), (p["length"], p["sha256"]), p["title"])
        for r in v["refused"]:
            with self.assertRaises(ValueError, msg=r["name"]):
                C.pack(bytes.fromhex(r["image"]) if "image" in r else bytes(r["length"]), "X")
        C.pack(bytes(v["max_ok_length"]), "X")
        for n in v["names"]:
            self.assertEqual((C.default_title(n["path"]), C.default_output(n["path"])), (n["title"], n["out"]))

    def test_board(self):
        """Which board: the table (rev0 and rev1 known, none reserved), the
        names, HELLO's board field, a bootloader image's board word, -device
        against an image, and pack's header for each board."""
        b = VECTORS["board"]
        self.assertEqual((C.DEVICES, C.RESERVED), (b["devices"], b["reserved"]))
        self.assertEqual((C.target_of("rev0"), C.target_of("rev1")), (C.TARGET_REV0, C.TARGET_REV1))
        self.assertEqual(C.known_devices(), b["known"])
        with self.assertRaises(ValueError) as cm:
            C.target_of("rev9")
        self.assertIn(f"(known: {b['known']})", str(cm.exception))
        for n in b["names"]:
            self.assertEqual(C.board_name(n["target"]), n["name"])
        for h in b["hello"]:
            parsed = P.Hello.parse(bytes.fromhex(h["payload"]))
            self.assertEqual((parsed.board, parsed.board_reported), (h["board"], h["reported"]))
        images = {c["name"]: bytes.fromhex(c["image"]) for c in b["boot_image"]}
        for c in b["boot_image"]:
            self.assertEqual(I.boot_image_board(images[c["name"]]), c["board"], c["name"])
        for c in b["device_check"]:
            try:
                I.check_boot_board(images[c["image"]], c["device"])
                ok = True
            except ValueError:
                ok = False
            self.assertEqual(ok, c["ok"], c)
        for p in b["packs"]:
            self.assertEqual(C.pack(bytes(64), "X", device=p["device"])[:C.HEADER_BYTES].hex(), p["header"], p["device"])

    def test_reserved_board(self):
        """No board is reserved now; one patched in for the test is refused by
        name everywhere a device is taken, as rev1 was before it was defined."""
        r = VECTORS["board"]["reserved_example"]
        self.assertNotIn(r["device"], C.DEVICES)
        with mock.patch.dict(C.RESERVED, {r["device"]: r["target"]}):
            self.assertEqual(C.board_name(r["target"]), r["name"])
            for refuse in (lambda: C.target_of(r["device"]), lambda: C.pack(bytes(64), "X", device=r["device"]),
                           lambda: I.check_boot_board(bytes(256), r["device"])):
                with self.assertRaises(ValueError) as cm:
                    refuse()
                self.assertIn("reserved for a board that is not defined yet", str(cm.exception))
        self.assertTrue(C.board_name(r["target"]).startswith("unknown board"))

    def test_wchisp(self):
        """What provision reads from wchisp's output."""
        for c in VECTORS["wchisp"]["probe"]:
            self.assertEqual(W.devices_in(c["output"]), c["devices"])
        for c in VECTORS["wchisp"]["info"]:
            self.assertEqual(W.uid_in(c["output"]) or "", c["uid"])

    def test_chg_matches_chgpack_and_the_header(self):
        """The repository's tools/chgpack.py and shared/chg_format.h say the same."""
        repo = HERE.parents[3]
        chgpack = repo / "tools" / "chgpack.py"
        if not chgpack.exists():
            self.skipTest("not in the CHGame repository")
        sys.path.insert(0, str(chgpack.parent))
        import chgpack as T  # noqa: E402
        app = bytes.fromhex(VECTORS["chg"]["app"])
        self.assertEqual(C.pack(app, "MY GAME", "ME", "1.2", 7), T.pack(app, "MY GAME", "ME", "1.2", 7))
        hdr = (HERE.parents[1] / "shared" / "chg_format.h").read_text(encoding="utf-8")
        self.assertEqual({T.BOARDS[t][0]: t for t in T.BOARDS}, C.DEVICES, "the boards chgpack and the uploader know")
        self.assertEqual({v: t for t, v in T.RESERVED.items()}, C.RESERVED, "the reserved boards")
        for name, val in (("CHG_MAGIC", C.MAGIC), ("CHG_TARGET_REV0", C.TARGET_REV0),
                          ("CHG_TARGET_REV1", C.TARGET_REV1), ("CHG_LAYOUT_ID", C.LAYOUT_ID),
                          ("CHG_HEADER_BYTES", C.HEADER_BYTES), ("CHG_FORMAT_VERSION", C.FORMAT_VERSION)):
            m = re.search(r"#define\s+" + name + r"\s+(0x[0-9A-Fa-f]+|\d+)u", hdr)
            self.assertIsNotNone(m, name)
            self.assertEqual(int(m.group(1), 0), val, name)


if __name__ == "__main__":
    unittest.main()
