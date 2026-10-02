"""layout.py (the uploader's mirror of the flash layout) against the C header
it mirrors, bootloader/src/chgame_map.h, read by tools/chgame_map.py."""
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
BOOT = HERE.parents[1]
sys.path.insert(0, str(BOOT / "host" / "py"))
sys.path.insert(0, str(BOOT / "tools"))
import chgame_map  # noqa: E402
from chgame_upload import layout as L  # noqa: E402


class Layout(unittest.TestCase):
    def test_mirror_matches_header(self):
        header = chgame_map.load()
        for name, value in L.as_dict().items():
            self.assertIn(name, header, f"{name} is not in chgame_map.h")
            self.assertEqual(value, header[name], name)

    def test_derived(self):
        self.assertEqual(L.APP_START, L.BOOT_START + L.BOOT_SIZE)
        self.assertEqual(L.META_ADDR, L.FLASH_SIZE - L.PAGE_SIZE)
        self.assertEqual(L.APP_MAX_SIZE, L.META_ADDR - L.APP_START)
        self.assertEqual(L.APP_MAX_SIZE, 50944)


if __name__ == "__main__":
    unittest.main()
