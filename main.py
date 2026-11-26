#!/usr/bin/env python3
"""Ship the finished front page to the grader's output folder.

The finished broadsheet lives in this repository as entry.png: a 680x1024
PNG drawn from real file photos and the verified news of Thursday
26 November 2026. This program is only a courier. It reads entry.png,
checks that it is really the PNG it expects — right magic bytes, right
dimensions, every chunk intact with a good CRC, no larger than the
competition allows — and then writes those exact bytes to entry.png in
the output directory (``/output`` by default, or ``MAKEFUN_OUTPUT_DIR``
when that is set). Standard library only, no network, no clock, no
randomness, so two runs always write identical bytes.
"""

import os
import struct
import sys
import zlib

EXPECTED_NAME = "entry.png"
EXPECTED_WIDTH = 680
EXPECTED_HEIGHT = 1024
BYTE_LIMIT = 1048576
BYTE_COUNT = 708709

MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(reason):
    """Stop without writing anything, explaining why."""
    print("main.py: refusing to write output: " + reason, file=sys.stderr)
    raise SystemExit(1)


def here():
    """The repository root, i.e. the directory holding this file."""
    return os.path.dirname(os.path.abspath(__file__))


def where_to_write():
    """The grader's output directory, honouring its override variable."""
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return wanted if wanted else "/output"


def load_image(path):
    """Read the source PNG, failing loudly on any filesystem problem."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        fail("no source image at " + path)
    except OSError as problem:
        fail("cannot read source image at " + path + ": " + str(problem))


def walk_chunks(data):
    """Check the PNG chunk by chunk; return the (width, height) in IHDR.

    Every chunk must fit inside the file and carry a CRC that matches its
    contents, and the file must end with a proper IEND chunk.
    """
    if len(data) < 8 or data[:8] != MAGIC:
        fail("source is not a PNG file (wrong magic bytes)")
    if len(data) != BYTE_COUNT:
        fail("source PNG is %d bytes, expected %d" % (len(data), BYTE_COUNT))

    pos = 8
    saw_ihdr = False
    saw_iend = False
    width = height = 0
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 8 + length + 4
        if end > len(data):
            fail("PNG chunk %r runs past the end of the file" % kind)
        body = data[pos + 8:pos + 8 + length]
        stored_crc, = struct.unpack(">I", data[pos + 8 + length:end])
        real_crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        if stored_crc != real_crc:
            fail("PNG chunk %r has a bad CRC" % kind)
        if kind == b"IHDR":
            if saw_ihdr or length != 13:
                fail("PNG has a bad IHDR chunk")
            saw_ihdr = True
            width, height = struct.unpack(">II", body[:8])
        if kind == b"IEND":
            saw_iend = True
            if end != len(data):
                fail("bytes follow the PNG IEND chunk")
            break
        pos = end
    if not saw_ihdr:
        fail("PNG has no IHDR chunk")
    if not saw_iend:
        fail("PNG has no IEND chunk")
    return width, height


def write_output(directory, data):
    """Write the bytes out, creating the output directory if needed."""
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as problem:
        fail("cannot create output directory " + directory + ": " + str(problem))
    target = os.path.join(directory, EXPECTED_NAME)
    try:
        with open(target, "wb") as handle:
            handle.write(data)
    except OSError as problem:
        fail("cannot write " + target + ": " + str(problem))
    return target


def run():
    source = os.path.join(here(), EXPECTED_NAME)
    data = load_image(source)
    width, height = walk_chunks(data)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail("source PNG is %dx%d, expected %dx%d"
             % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))
    if len(data) > BYTE_LIMIT:
        fail("source PNG is %d bytes, over the %d limit"
             % (len(data), BYTE_LIMIT))
    target = write_output(where_to_write(), data)
    print("main.py: wrote %d bytes to %s" % (len(data), target))


if __name__ == "__main__":
    run()
