#!/bin/bash
cd "$(dirname "$0")"
clear
echo "=== Mini Linux (persistent data disk /data) ==="
echo "memory: 512M   (override: ML_MEM_DATA=1G ./boot.sh data)"
echo "exit: type poweroff -f"
echo
exec ./boot.sh data
