#!/bin/bash
# Mini Linux boot script (macOS)
# Usage:
#   ./boot.sh            boot kernel directly (serial console, recommended)
#   ./boot.sh iso        boot from mini-linux.iso (serial console)
#   ./boot.sh vga        boot from mini-linux-vga.iso (VGA window)
#   ./boot.sh data       boot with persistent data disk (virtio, /data)
# Memory can be overridden:  ML_MEM=1G ./boot.sh data
# Type "poweroff -f" inside the guest to shut down.

DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
QEMU="$ROOT/tools/qemu-launcher"
PCBIOS="$ROOT/tools/UTM.app/Contents/Resources/qemu"
ISO="$DIR/mini-linux.iso"
ISO_VGA="$DIR/mini-linux-vga.iso"
KERNEL="$DIR/vmlinuz"
INITRD="$DIR/initramfs.cpio.gz"
INITRD_DATA="$DIR/initramfs-data.cpio.gz"
DISK="$DIR/mini-linux-data.img"
MEM="${ML_MEM:-256M}"          # default memory for all modes
MEM_DATA="${ML_MEM_DATA:-512M}" # data mode gets more room

if [ ! -x "$QEMU" ]; then
    echo "ERROR: qemu launcher not found at: $QEMU" >&2
    exit 1
fi
if [ ! -d "$PCBIOS" ]; then
    echo "ERROR: pc-bios dir not found at: $PCBIOS" >&2
    exit 1
fi

case "$1" in
    iso)
        [ -f "$ISO" ] || { echo "ERROR: $ISO missing" >&2; exit 1; }
        exec "$QEMU" -m "$MEM" -cdrom "$ISO" -boot d \
            -nographic -no-reboot -L "$PCBIOS" ;;
    vga)
        [ -f "$ISO_VGA" ] || { echo "ERROR: $ISO_VGA missing" >&2; exit 1; }
        exec "$QEMU" -m "$MEM" -cdrom "$ISO_VGA" -boot d \
            -no-reboot -L "$PCBIOS" ;;
    data)
        [ -f "$INITRD_DATA" ] || { echo "ERROR: $INITRD_DATA missing" >&2; exit 1; }
        [ -f "$DISK" ] || { echo "ERROR: $DISK missing" >&2; exit 1; }
        exec "$QEMU" -m "$MEM_DATA" -kernel "$KERNEL" -initrd "$INITRD_DATA" \
            -drive file="$DISK",format=raw,if=virtio \
            -nographic -no-reboot -L "$PCBIOS" \
            -append "console=ttyS0 data" ;;
    *)
        [ -f "$KERNEL" ] && [ -f "$INITRD" ] || { echo "ERROR: $KERNEL or $INITRD missing" >&2; exit 1; }
        exec "$QEMU" -m "$MEM" -kernel "$KERNEL" \
            -initrd "$INITRD" \
            -nographic -no-reboot -L "$PCBIOS" \
            -append "console=ttyS0" ;;
esac
