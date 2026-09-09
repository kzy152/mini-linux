#!/usr/bin/env python3
"""Generate a 1024x1024 pixel-art terminal icon for Mini Linux (no deps)."""
import struct, zlib, sys

S = 32                 # logical grid
SCALE = 32             # 32*32 = 1024
W = H = S * SCALE

def px(g, x, y, color):
    if 0 <= x < S and 0 <= y < S:
        g[y][x] = color

def round_rect(g, x0, y0, x1, y1, r, color):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            # distance to nearest corner circle center
            cx = x0 + r if x < x0 + r else (x1 - r if x > x1 - r else x)
            cy = y0 + r if y < y0 + r else (y1 - r if y > y1 - r else y)
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            px(g, x, y, color)

def thick_line(g, x0, y0, x1, y1, w, color):
    """Bresenham line with thickness w."""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for oy in range(-(w // 2), w - w // 2):
            for ox in range(-(w // 2), w - w // 2):
                px(g, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy

GREEN = (74, 222, 128)
DARK  = (26, 27, 38)
BLACK = (13, 13, 20)
GRAY  = (90, 96, 120)

g = [[DARK for _ in range(S)] for _ in range(S)]
# window frame with green border
round_rect(g, 1, 1, S - 2, S - 2, 6, (44, 46, 62))
round_rect(g, 3, 3, S - 4, S - 4, 4, BLACK)
# title bar dots
for dx, c in ((0, GRAY), (4, GRAY), (8, GRAY)):
    px(g, 6 + dx, 6, c)
# prompt ">_"
thick_line(g, 8, 12, 12, 16, 2, GREEN)   # > top stroke
thick_line(g, 12, 16, 8, 20, 2, GREEN)   # > bottom stroke
thick_line(g, 15, 20, 21, 20, 2, GREEN)  # _
# blinking cursor block
for y in range(13, 20):
    for x in range(23, 27):
        px(g, x, y, GREEN)

# scale up and write PNG
img = bytearray()
for y in range(S):
    row = [0] * (W * 3)
    for yy in range(SCALE):
        for x in range(S):
            r, gr, b = g[y][x]
            for xx in range(SCALE):
                i = (x * SCALE + xx) * 3
                row[i] = r; row[i + 1] = gr; row[i + 2] = b
        img.append(0)  # filter: none
        img.extend(bytes(row))

def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return c

png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(bytes(img), 9))
png += chunk(b"IEND", b"")

out = sys.argv[1] if len(sys.argv) > 1 else "icon.png"
with open(out, "wb") as f:
    f.write(png)
print(f"wrote {out}: {W}x{H} ({len(png)} bytes)")
