<pir>
<meta>
name: my_os
root: /home/user/projects/my_os
profile: os-riscv
lang: C,ASM,LD
</meta>

<units>
u0: core/init.c type=C role=kernel module=core
u1: mm/page.c type=C role=mm module=mm
u2: boot/start.S type=ASM role=entry module=boot
u3: linker/os.ld type=LD role=linkscript module=link
</units>

<dependencies>
u2->call:u0#start_kernel
u0->call:u1#page_init
u0->include:u3
u0->include:[stdio.h]
u1->use:u0#[PAGE_SIZE]
</dependencies>

<symbols>
start_kernel:u0 func entry=true
page_init:u1 func
_bss_start:u3 ld
_bss_end:u3 ld
PAGE_SIZE:u0 macro
</symbols>

<layout>
ENTRY=start_kernel
BASE=0x80000000
.text:u2 u0
.rodata:u0
.data:u0
.bss:u1 u0
</layout>

<code-snippets>
<snippet unit="u2">
<![CDATA[
    .section .text
    .globl _start
_start:
    csrr t0, mhartid
    bnez t0, park
    j start_kernel
park:
    wfi
    j park
]]>
</snippet>
<snippet unit="u0">
<![CDATA[
#include <stdio.h>
#define PAGE_SIZE 4096
void start_kernel() {
    printf("Booting kernel...\n");
    page_init();
    while (1) {
        // Kernel main loop...
    }
}
]]>
</snippet>
</code-snippets>
</pir>

