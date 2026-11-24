#!/usr/bin/env python3
"""Entrypoint for the news-image-20261124 entry.

Validates the bundled entry.png as a whole, well-formed PNG within the
competition limits, then copies it byte for byte to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png). Standard library only, no network,
and the output is identical on every run because the input bytes are
copied unchanged.
"""

import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")

MAX_BYTES = 1048576          # 1 MiB
MAX_DIM = 1024               # 1024 x 1024 pixels
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def read_png(path):
    """Read and gate-check a PNG file. Returns (width, height, data)."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")

    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")

    pos = 8
    width = height = None
    seen_ihdr = False
    seen_iend = False
    idat_total = 0
    while pos < len(data):
        if pos + 8 > len(data):
            fail("truncated PNG chunk header")
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if pos + 12 + length > len(data):
            fail(f"truncated PNG chunk {ctype!r}")
        chunk_data = data[pos + 8:pos + 8 + length]
        (crc_stored,) = struct.unpack(
            ">I", data[pos + 8 + length:pos + 12 + length])
        crc_actual = zlib.crc32(ctype)
        crc_actual = zlib.crc32(chunk_data, crc_actual) & 0xFFFFFFFF
        if crc_actual != crc_stored:
            fail(f"bad CRC in PNG chunk {ctype!r}")
        if ctype == b"IHDR":
            if seen_ihdr:
                fail("duplicate IHDR chunk")
            if length != 13:
                fail("IHDR chunk has the wrong length")
            (width, height, bit_depth, colour_type, compression,
             filtering, interlace) = struct.unpack(">IIBBBBB", chunk_data)
            if compression != 0 or filtering != 0:
                fail("unsupported PNG compression or filter method")
            if interlace != 0:
                fail("interlaced PNGs are not accepted by this gate")
            if bit_depth not in (1, 2, 4, 8, 16):
                fail(f"unsupported PNG bit depth {bit_depth}")
            if colour_type not in (0, 2, 3, 4, 6):
                fail(f"unsupported PNG colour type {colour_type}")
            if width < 1 or height < 1:
                fail("PNG has a zero dimension")
            if width > MAX_DIM or height > MAX_DIM:
                fail(f"image is {width}x{height}, over the 1024x1024 limit")
            seen_ihdr = True
        elif ctype == b"IDAT":
            idat_total += length
        elif ctype == b"IEND":
            if length != 0:
                fail("IEND chunk is not empty")
            seen_iend = True
            pos += 12 + length
            break
        pos += 12 + length

    if not seen_ihdr:
        fail("PNG has no IHDR chunk")
    if not seen_iend:
        fail("PNG has no IEND chunk")
    if pos != len(data):
        fail("trailing bytes after the PNG IEND chunk")
    if idat_total == 0:
        fail("PNG has no image data (no IDAT chunk)")

    # The header must match the image data: decompress and check that the
    # raw scanlines are exactly the size the header describes.
    raw = b"".join(
        _idat_chunks(data))
    try:
        pixels = zlib.decompress(raw)
    except zlib.error as exc:
        fail(f"PNG image data does not decompress: {exc}")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour_type]
    bits_per_pixel = channels * bit_depth
    row_bits = width * bits_per_pixel
    row_bytes = (row_bits + 7) // 8
    expected = height * (1 + row_bytes)
    if len(pixels) != expected:
        fail(f"image data is {len(pixels)} bytes, header implies "
             f"{expected} bytes")

    return width, height, data


def _idat_chunks(data):
    """Yield the payload of every IDAT chunk in order."""
    pos = 8
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if ctype == b"IDAT":
            yield data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IEND":
            break


def main():
    width, height, data = read_png(SRC)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as fh:
        fh.write(data)
    print(f"wrote {out_path} ({width}x{height}, {len(data)} bytes)")


if __name__ == "__main__":
    main()
