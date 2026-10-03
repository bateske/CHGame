"""The Python uploader against the shared vectors (vectors.json), and the
vectors file against what the package computes now.

    python -m unittest discover -s platform/bootloader/test/protocol -v
"""
import hashlib
import json
import pathlib
import struct
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "host" / "py"))
from chgame_upload import image as I, layout as L, protocol as P, upload as U, vectors as V  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
