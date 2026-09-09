# Mini Linux —— 一个能启动的迷你 Linux 系统

手工搭建的最小可启动 Linux：**Linux 内核 + busybox 根文件系统（initramfs）**，产出可直接启动的 CD 镜像（ISO）。已在 QEMU 中完成真实启动验证。

## 产物（dist/）

| 文件 | 说明 | 大小 |
|---|---|---|
| `mini-linux.iso` | 可启动光盘镜像（BIOS + ISOLINUX 6.04 引导，串口控制台，适合无头场景） | 12 MB |
| `mini-linux-vga.iso` | 同上，但控制台走 VGA 图形界面 | 12 MB |
| `vmlinuz` | Linux 6.6.134-0-lts 内核（x86_64 bzImage，Alpine 官方构建） | 10 MB |
| `initramfs.cpio.gz` | 根文件系统：busybox 1.36.1（静态链接） + 自写 `/init` | 622 KB |
| `initramfs-data.cpio.gz` | 数据版根文件系统：含 kmod + virtio/vfat 模块，支持持久数据盘 | 3.9 MB |
| `mini-linux-data.img` | 64 MiB FAT16 持久数据盘（label MINILINUX，启动后挂载到 `/data`） | 64 MB |
| `boot.sh` | 一键启动脚本（macOS，走本目录内置的 QEMU；`ML_MEM`/`ML_MEM_DATA` 可覆盖内存） | — |
| `mini-linux.command` | 终端双击启动脚本（data 模式） | — |
| `README.md` | 本文档 | — |
| `evidence/` | 4 次真实启动验证的日志与截图 | — |

## 启动方式

### 桌面 APP（最简单）
桌面上有 **Mini Linux.app**：双击后自动打开终端窗口，以 512 MB 内存 + 持久数据盘（`/data`）启动。
关机在系统内输入 `poweroff -f`。

### 本机（macOS）最快方式
```bash
cd ~/mini-linux
./dist/boot.sh          # 内核直启（串口，256M）
./dist/boot.sh iso      # 光盘启动（串口，256M）
./dist/boot.sh vga      # 光盘启动（VGA 窗口，256M）
./dist/boot.sh data     # 持久数据盘模式（virtio /data，512M）
ML_MEM=1G ./dist/boot.sh        # 任意模式可用环境变量覆盖内存
```
看到 `MINI LINUX BOOTED OK` 与 `mini-linux:/#` 提示符即成功，输入 `poweroff -f` 关机。

### 持久数据盘（data 模式）
- 数据盘 `mini-linux-data.img`（FAT16，64 MiB）以 virtio 块设备接入，系统内挂载到 `/data`；
- 写入 `/data` 的文件在关机/重启后保留；init 每次启动向 `/data/bootlog.txt` 追加一条记录；
- 模块加载采用 insmod 显式按依赖顺序加载（Alpine 精简版 kmod 的 modprobe 名字解析在该环境不可用，已实测确认）。

> 说明：这台 Mac 的 Homebrew 已不再支持 macOS 13（无预编译包），无法 `brew install qemu`。
> 项目内置了从 UTM 官方 dmg 提取的 QEMU 10.0.2 二进制，并用一个 15 行的 C 加载器
> （`tools/qemu-launcher.c`，dlopen 动态库后调用 qemu_init/qemu_main_loop）运行。
> 若你换了支持 brew 的系统，`brew install qemu` 后可用标准命令：
> ```bash
> qemu-system-x86_64 -m 256M -cdrom mini-linux.iso -boot d -nographic
> ```

### 真实硬件 / 写入 U 盘
ISO 是标准 El Torito BIOS 启动盘。刻录或 `dd` 写入 U 盘（**会清空目标盘，务必先确认设备号**）：
```bash
# sudo dd if=mini-linux.iso of=/dev/diskX bs=4m conv=sync
```

## 系统内部结构

```
initramfs.cpio.gz
├── init          # PID 1 启动脚本（自写）：
│                 #   挂载 /proc /sys /dev → 打印横幅 → 启动 shell；
│                 #   支持 autoshutdown 内核参数（CI 自动关机）；
│                 #   无串口控制台时自动在 ttyS0 额外开一个 shell
├── bin/
│   ├── busybox   # 静态链接 x86_64 busybox 1.36.1（Alpine 官方构建）
│   └── sh ash cat ls mount umount poweroff reboot uname dmesg df
│       free ps kill grep head tail setsid hostname vi tar gzip ...  # 33 个符号链接
├── dev/console   # c 5 1
├── dev/null      # c 1 3
├── proc/ sys/    # 挂载点
```

ISO 布局：`/boot/vmlinuz`、`/boot/initramfs.gz`、`/isolinux/*`（isolinux.bin 为 El Torito 引导镜像，配置 `APPEND console=ttyS0` 或 `console=tty0`）。

## 构建配方（可复现）

```bash
# 1. initramfs（任意 Linux/macOS）
cd rootfs/initramfs && find . | cpio -o -H newc | gzip -9 > ../../dist/initramfs.cpio.gz

# 2. ISO（需要 xorriso；isolinux 文件取自 Alpine syslinux 包）
mkdir -p iso/{isolinux,boot}
cp dist/vmlinuz iso/boot/ && cp dist/initramfs.cpio.gz iso/boot/initramfs.gz
cp src/syslinux/usr/share/syslinux/{isolinux.bin,ldlinux.c32,libcom32.c32,libutil.c32} iso/isolinux/
# iso/isolinux/isolinux.cfg:
#   DEFAULT mini / LABEL mini / LINUX /boot/vmlinuz / INITRD /boot/initramfs.gz / APPEND console=ttyS0
xorriso -as mkisofs -o mini-linux.iso -V MINILINUX \
  -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table \
  -c isolinux/boot.cat iso/
```

素材来源（已随项目保留在 `src/`）：
- 内核：Alpine Linux 官方 netboot `vmlinuz-lts`（Linux 6.6.134，x86_64）
- busybox：Alpine `busybox-static-1.36.1-r31.apk`（静态链接）
- syslinux：Alpine `syslinux-6.04_pre1-r15.apk`

## 验证记录（evidence/）

| 测试 | 方式 | 结果 |
|---|---|---|
| 内核直启 + 自动关机 | `qemu -kernel/-initrd -append "console=ttyS0 autoshutdown"` | ✅ 横幅、挂载、关机正常 |
| 交互式 shell | 串口输入 echo/uname/ls/hostname/poweroff | ✅ 全部回显正确 |
| ISO 光盘启动（串口） | `qemu -cdrom mini-linux.iso -boot d` | ✅ SeaBIOS→ISOLINUX→内核→shell |
| ISO 光盘启动（VGA 截图） | `qemu -cdrom mini-linux-vga.iso` + screendump | ✅ 截图见 evidence/ |

## 已知取舍

- **内核未自编译**：原计划用 clang/LLVM 从源码交叉编译最小内核，但该机器 Homebrew 已放弃
  macOS 13（所有包无 bottle、只能源码编译，llvm 需数小时），故采用 Alpine 官方 LTS 内核
  （发行版同款做法：内核用现成、系统自建）。若在受支持的 macOS/Linux 上，`README` 保留了
  自编译的完整命令思路（见 git 历史或询问）。
- 无网络、无磁盘驱动需求：根文件系统全部在内存 initramfs 中，无需任何块设备驱动即可启动。
- `sh: can't access tty` 提示是 init 无控制终端所致，功能不受影响；需要完整 job control 可在
  内核参数加 `console=ttyS0` 并用 getty 替代。
