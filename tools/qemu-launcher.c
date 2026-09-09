// qemu-launcher.c — 加载 UTM 打包的 qemu 动态库并执行
// 用法: qemu-launcher [qemu 参数...]
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

extern char **environ;

typedef void (*qemu_init_fn)(int, char **, char **);
typedef void (*qemu_main_loop_fn)(void);
typedef void (*qemu_cleanup_fn)(void);

int main(int argc, char **argv) {
    void *h = dlopen("/Users/macbook/mini-linux/tools/UTM.app/Contents/Frameworks/"
                     "qemu-x86_64-softmmu.framework/Versions/A/qemu-x86_64-softmmu",
                     RTLD_NOW | RTLD_GLOBAL);
    if (!h) {
        fprintf(stderr, "dlopen qemu failed: %s\n", dlerror());
        return 127;
    }
    qemu_init_fn init = (qemu_init_fn)dlsym(h, "qemu_init");
    qemu_main_loop_fn loop = (qemu_main_loop_fn)dlsym(h, "qemu_main_loop");
    qemu_cleanup_fn cleanup = (qemu_cleanup_fn)dlsym(h, "qemu_cleanup");
    if (!init || !loop || !cleanup) {
        fprintf(stderr, "dlsym failed: %s\n", dlerror());
        return 127;
    }
    init(argc, argv, environ);
    loop();
    cleanup();
    return 0;
}
