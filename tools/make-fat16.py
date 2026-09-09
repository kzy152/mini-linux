#!/usr/bin/env python3
"""生成 64MiB FAT16 数据盘镜像（纯 Python，无外部依赖）。"""
import struct, sys, os, time

def fat16_make(path, size_mb=64, label="MINILINUX", file_entries=None):
    SECTOR = 512
    total_sectors = size_mb * 1024 * 1024 // SECTOR
    SPC = 8                      # sectors per cluster
    reserved = 1                 # boot sector
    fats = 2
    root_entries = 512           # FAT16 root dir: 512 entries
    root_sectors = root_entries * 32 // SECTOR

    # 计算 FAT 大小（收敛）
    def fat_sectors_for(clusters):
        return (clusters + 2) * 2 // SECTOR + 1
    clusters = (total_sectors - reserved - root_sectors) // SPC
    fs = fat_sectors_for(clusters)
    # 重算（FAT 本身占用数据区）
    while True:
        data_sectors = total_sectors - reserved - fats * fs - root_sectors
        c2 = data_sectors // SPC
        f2 = fat_sectors_for(c2)
        if f2 == fs and c2 <= 0xFFF5:
            clusters = c2; break
        fs = f2

    data_start = reserved + fats * fs + root_sectors
    cluster_sectors = clusters * SPC

    img = bytearray(total_sectors * SECTOR)

    # ---- BPB (FAT16) ----
    bpb = bytearray(512)
    bpb[0:3] = b"\xeb\x3c\x90"                    # jmp + nop
    bpb[3:11] = b"MINILINUX"                      # OEM (8 bytes)
    struct.pack_into("<H", bpb, 11, SECTOR)        # bytes per sector
    struct.pack_into("<B", bpb, 13, SPC)           # sectors per cluster
    struct.pack_into("<H", bpb, 14, reserved)      # reserved sectors
    struct.pack_into("<B", bpb, 16, fats)          # number of FATs
    struct.pack_into("<H", bpb, 17, root_entries)  # root entries
    struct.pack_into("<H", bpb, 19, 0)             # total sectors 16 (0 -> use 32)
    struct.pack_into("<B", bpb, 21, 0xF8)          # media descriptor
    struct.pack_into("<H", bpb, 22, fs)            # FAT size 16
    struct.pack_into("<H", bpb, 24, 32)            # sectors per track
    struct.pack_into("<H", bpb, 26, 64)            # heads
    struct.pack_into("<I", bpb, 28, 0)             # hidden sectors
    struct.pack_into("<I", bpb, 32, total_sectors) # total sectors 32
    struct.pack_into("<B", bpb, 36, 0x80)          # drive number
    struct.pack_into("<B", bpb, 37, 0)             # reserved
    struct.pack_into("<B", bpb, 38, 0x29)          # boot signature
    struct.pack_into("<I", bpb, 39, 0x20260909)    # volume id
    bpb[43:54] = (label + "           ")[:11].encode()   # volume label
    bpb[54:62] = b"FAT16   "                      # fs type
    bpb[510:512] = b"\x55\xaa"
    img[0:SECTOR] = bpb

    # ---- FAT 表 ----
    fat = bytearray(fs * SECTOR)
    fat[0:4] = struct.pack("<HH", 0xFFF8, 0xFFFF)  # FAT[0], FAT[1]
    def set_fat(entry, val):
        off = entry * 2
        struct.pack_into("<H", fat, off, val)

    # 文件分配：链式分配集群
    next_cluster = 2
    def alloc_cluster_chain(n):
        nonlocal next_cluster
        first = next_cluster
        for i in range(n):
            c = next_cluster + i
            set_fat(c, (c + 1) if i < n - 1 else 0xFFFF)
        next_cluster += n
        return first

    # ---- 根目录 + 文件数据 ----
    root = bytearray(root_sectors * SECTOR)
    def make_dirent(name, attr, first_cluster, size, ctime):
        e = bytearray(32)
        e[0:11] = name.encode('ascii')
        e[11] = attr
        # date/time: 使用固定值 (2026-09-09 12:00:00)
        d = ((2026 - 1980) << 9) | (9 << 5) | 9
        t = (12 << 11) | (0 << 5) | 0
        struct.pack_into("<H", e, 14, t)
        struct.pack_into("<H", e, 16, d)
        struct.pack_into("<H", e, 18, d)
        struct.pack_into("<H", e, 20, t)
        struct.pack_into("<H", e, 22, (first_cluster >> 16) & 0xFFFF)
        struct.pack_into("<H", e, 26, first_cluster & 0xFFFF)
        struct.pack_into("<I", e, 28, size)
        return e

    entry_off = 0
    if file_entries:
        for name, content in file_entries:
            nclusters = (len(content) + SPC * SECTOR - 1) // (SPC * SECTOR)
            first = alloc_cluster_chain(nclusters)
            # 写入第二个 FAT（两表一致）
            # 数据区写入
            base = data_start + (first - 2) * SPC
            img[base * SECTOR : base * SECTOR + len(content)] = content
            root[entry_off:entry_off+32] = make_dirent(name, 0x20, first, len(content), None)
            entry_off += 32

    img[reserved * SECTOR : (reserved + fs) * SECTOR] = fat
    img[(reserved + fs) * SECTOR : (reserved + 2*fs) * SECTOR] = fat  # FAT 2
    img[(reserved + 2*fs) * SECTOR : (reserved + 2*fs + root_sectors) * SECTOR] = root

    with open(path, "wb") as f:
        f.write(img)
    print(f"OK: {path} {size_mb}MiB, clusters={clusters}, FAT sectors={fs}, data_start={data_start}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/mini-linux-data.img"
    fat16_make(out, file_entries=[
        ("HELLO   TXT", b"Hello from Mini Linux data disk!\n"
                        b"This file is stored on the persistent disk image.\n"
                        b"Write more files into /data inside the VM.\n"),
    ])
