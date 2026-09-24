#!/bin/bash
cd "$(dirname "$0")"
clear
echo "=== Mini Linux (desktop: X + openbox, persistent /data) ==="
echo "memory: 512M   (override: ML_MEM_DATA=1G ./boot.sh data gui)"
echo "exit: type poweroff -f in a terminal, or use the desktop menu"
echo
exec ./boot.sh data gui
