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

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "host" / "py"))
from chgame_upload import chg as C, image as I, layout as L, protocol as P, upload as U, vectors as V  # noqa: E402

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
        for name, val in (("CHG_MAGIC", C.MAGIC), ("CHG_TARGET_ID", C.TARGET_ID), ("CHG_LAYOUT_ID", C.LAYOUT_ID),
                          ("CHG_HEADER_BYTES", C.HEADER_BYTES), ("CHG_FORMAT_VERSION", C.FORMAT_VERSION)):
            m = re.search(r"#define\s+" + name + r"\s+(0x[0-9A-Fa-f]+|\d+)u", hdr)
            self.assertIsNotNone(m, name)
            self.assertEqual(int(m.group(1), 0), val, name)


if __name__ == "__main__":
    unittest.main()
