<pir>
<meta>
name: my_os
root: /home/user/projects/my_os
profile: os-riscv
lang: C,ASM,LD
</meta>

<units>
u0: core/init.c type=C role=entry module=core
u1: mm/page.c type=C role=mm module=mm
u2: boot/start.S type=ASM role=boot module=boot
</units>

<dependency-pool>
d0: call:u0#start_kernel
d1: call:u1#page_init
d2: include:[stdio.h]
</dependency-pool>

<dependencies>
u2->refs:[d0]
u0->refs:[d1 d2]
</dependencies>

<symbols>
start_kernel:u0 func entry=true
page_init:u1 func
</symbols>

<layout>
ENTRY=start_kernel
BASE=0x80000000
.text: u2 u0
.data: u0 u1
</layout>
</pir>
