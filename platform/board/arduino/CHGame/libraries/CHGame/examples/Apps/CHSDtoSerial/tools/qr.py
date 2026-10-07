"""The website's QR code as a table in flash: the sketch's Qr.h.

    python tools/qr.py [URL]

Encodes the address (default https://play.chgame.website) as a version 2
QR code (25 x 25 modules, error correction L) with the `qrcode` package
(pip install qrcode), packs the modules a row at a time, MSB first, and
writes the header. The sketch draws it from the table, so the package is
needed only to remake it. With opencv installed the table is decoded back
as a check.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = sys.argv[1] if len(sys.argv) > 1 else "https://play.chgame.website"


def main():
    import qrcode
    q = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
    q.add_data(URL)
    q.make(fit=False)
    m = q.get_matrix()
    n = len(m)
    assert n == 25, n
    bits = [1 if cell else 0 for row in m for cell in row]
    packed = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for k, v in enumerate(bits[i:i + 8]):
            b |= v << (7 - k)
        packed.append(b)
    rows = []
    for i in range(0, len(packed), 16):
        rows.append("    " + ", ".join(f"0x{b:02X}" for b in packed[i:i + 16]) + ",")
    text = f"""/* SPDX-License-Identifier: GPL-3.0-or-later
 * The website's address as a QR code: version 2 (25 x 25 modules, error
 * correction L), the modules packed a row at a time, MSB first. Made by
 * tools/qr.py; not edited by hand.
 */
#pragma once
#include <stdint.h>
#define QR_URL "{URL}"
#define QR_LABEL "{URL.split('//', 1)[-1]}"
#define QR_TITLE "{URL.split('//', 1)[-1].upper()}"
#define QR_SIZE {n}
static const uint8_t QR_BITS[{len(packed)}] = {{
{chr(10).join(rows)}
}};
"""
    out = ROOT / "Qr.h"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"{out}: {n}x{n}, {len(packed)} bytes")
    try:
        import cv2
        import numpy as np
    except ImportError:
        return 0
    scale, quiet = 8, 4
    img = np.full(((n + 2 * quiet) * scale, (n + 2 * quiet) * scale), 255, np.uint8)
    for y in range(n):
        for x in range(n):
            if bits[y * n + x]:
                img[(y + quiet) * scale:(y + quiet + 1) * scale, (x + quiet) * scale:(x + quiet + 1) * scale] = 0
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    if text != URL:
        raise SystemExit(f"the table does not decode back to the address: {text!r}")
    print(f"decodes to {text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
