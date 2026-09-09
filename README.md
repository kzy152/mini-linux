# Mini Linux

从零手工搭建、可在 QEMU 中真实启动的迷你 Linux 系统：**Alpine LTS 内核 + busybox 根文件系统 + 自写 init**，另附**持久化数据盘**与**桌面启动器**。

![Mini Linux 启动画面](dist/evidence/boot-vga-screenshot.png)

## 特性

- **真实可启动**：Linux 6.6.134-0-lts 内核 + busybox 1.36.1（静态链接） + 自写 `/init`，已通过内核直启、串口交互、ISO 光盘、VGA 截图四轮验证
- **持久数据盘**：64 MiB FAT16 虚拟磁盘以 virtio 接入，挂载到 `/data`，关机/重启后数据保留
- **零安装依赖**：内置 QEMU 10.0.2 运行环境（Apple Silicon Mac，无 Homebrew 包可用场景下从 UTM 提取），无需 `brew install`
- **多模式启动**：内核直启（串口）/ ISO 光盘（串口）/ ISO 光盘（VGA）/ 数据盘模式
- **桌面 APP**：`Mini Linux.app` 双击即启动（自动开终端窗口，512M 内存 + 数据盘）

## 快速开始（macOS）

```bash
cd ~/mini-linux
./dist/boot.sh          # 内核直启（串口，256M）
./dist/boot.sh iso      # 光盘启动（串口）
./dist/boot.sh vga      # 光盘启动（VGA 窗口）
./dist/boot.sh data     # 持久数据盘模式（/data，512M）
ML_MEM=1G ./dist/boot.sh        # 任意模式可用环境变量覆盖内存
```

看到 `MINI LINUX BOOTED OK` 与 `mini-linux:/#` 提示符即成功，输入 `poweroff -f` 关机。

### 桌面 APP

桌面的 **Mini Linux.app** 双击即用：自动打开终端窗口，以 512M 内存 + 持久数据盘启动。

### 持久数据盘

```sh
# 数据盘模式启动后，写入 /data 的文件重启后仍在
echo "hello" > /data/secret.txt
sync
poweroff -f
# 再次启动后：
cat /data/secret.txt        # hello
tail /data/bootlog.txt      # 每次启动追加一条记录
```

## 目录结构

```
mini-linux/
├── dist/               # 产物：vmlinuz、initramfs*.cpio.gz、mini-linux*.iso、
│                       #       mini-linux-data.img、boot.sh、evidence/（验证证据）
├── rootfs/initramfs/   # 根文件系统源：自写 init + busybox 链接 + 模块子集
├── tools/              # qemu-launcher（自写 C 加载器）、make-fat16.py、make-icon.py
├── iso/                # ISO 组装暂存
├── build/              # 构建副本
└── src/                # 第三方素材（内核/initramfs 官方包，可重新下载）
```

## 构建与复现

完整构建配方见 [dist/README.md](dist/README.md)（initramfs 打包、ISO 制作、FAT16 镜像生成、模块选取）。

## 验证记录

| 测试 | 结果 |
|---|---|
| 内核直启 + 自动关机（`autoshutdown`） | ✅ |
| 串口交互式 shell（echo/uname/poweroff） | ✅ |
| ISO 光盘启动（SeaBIOS → ISOLINUX → 内核） | ✅ |
| ISO VGA 启动（截图） | ✅ |
| virtio 数据盘挂载 `/data`（insmod 链加载模块） | ✅ |

日志与截图见 `dist/evidence/`。

## 许可证

- **自写部分**（init、boot.sh、qemu-launcher、构建脚本、文档）：[GPL-3.0](LICENSE)
- **第三方组件**（Linux 内核、busybox、syslinux、QEMU、kmod 等）：各自保留原许可证，见 [THIRD_PARTY.md](THIRD_PARTY.md)
- 素材来源：Alpine Linux 官方构建（内核/netboot/initramfs）、UTM 官方包（QEMU 运行环境）

## 已知取舍

- 内核未自编译：采用发行版同款做法（内核用 Alpine 官方 LTS 构建，系统自建）；该机器 Homebrew 已放弃 macOS 13，无法快速源码构建 llvm/qemu
- 根文件系统为 initramfs（内存盘），无需块设备驱动即可启动；数据盘模式需加载 virtio/vfat 模块（insmod 按依赖顺序显式加载，Alpine 精简 kmod 的 modprobe 名字解析在该环境不可用）
