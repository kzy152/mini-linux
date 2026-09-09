# 第三方组件与许可证声明（Third-Party Notices）

本项目仓库采用**分层许可**：仓库根目录的 `LICENSE`（GPL-3.0）仅覆盖**本项目自写部分**；
随仓库分发的第三方二进制/文件**保留其各自原许可证**，详见下表。

> 提示：各组件许可以其官方仓库/包内自带许可证文件为准，下表为发布时的归纳整理。

| 组件 | 来源 | 许可证 | 说明 |
|---|---|---|---|
| Linux 内核 `vmlinuz-lts`（6.6.134-0-lts，x86_64） | Alpine Linux 官方 netboot 构建 | **GPL-2.0-only** | 与 GPL-3.0 不兼容，须保持原许可分发 |
| Linux 内核模块（`.ko`，随内核） | 同上（Alpine `initramfs-lts`） | **GPL-2.0-only** | 同上 |
| busybox 1.36.1（静态链接） | Alpine `busybox-static` 包 | **GPL-2.0-only** | busybox 项目明确为 GPL-2.0-only |
| syslinux / isolinux 6.04 | Alpine `syslinux` 包 | **GPL-2.0**（含例外条款） | ISO 引导 |
| QEMU 10.0.2（`qemu-x86_64-softmmu` 及 pc-bios） | 从 UTM 4.7.5 官方 dmg 提取（本项目未编译） | 主体 **GPL-2.0-or-later**；库组件 LGPL-2.1-or-later；pc-bios 固件各自许可（如 SeaBIOS LGPL-3.0） | 仅随本仓库的构建脚本使用，不并入 GPL-3.0 |
| kmod（含 modprobe/insmod 兼容入口） | Alpine `initramfs-lts` | **LGPL-2.1-or-later** | 动态链接分发 |
| libzstd | 上游 zstd 项目 | **BSD-3-Clause** | kmod 依赖 |
| liblzma（xz utils） | 上游 xz 项目 | **0BSD** | kmod 依赖 |
| zlib | 上游 zlib 项目 | **zlib License** | kmod 依赖 |
| OpenSSL libcrypto | 上游 OpenSSL 项目 | **Apache-2.0** | kmod 依赖 |

## 自写部分（GPL-3.0，随 `LICENSE` 分发）

- `rootfs/initramfs/init`（PID 1 启动脚本）
- `tools/qemu-launcher.c` 及编译出的 `tools/qemu-launcher`
- `tools/make-fat16.py`、`tools/make-icon.py`
- `dist/boot.sh`、`dist/mini-linux.command`
- `README.md`、`THIRD_PARTY.md` 等文档

## 获取第三方组件的官方来源

- Alpine Linux netboot：<https://alpinelinux.org/downloads/>（v3.20，`vmlinuz-lts` / `initramfs-lts`）
- UTM（QEMU 运行环境来源）：<https://mac.getutm.app/>
- GNU GPL-3.0 全文：<https://www.gnu.org/licenses/gpl-3.0.txt>
