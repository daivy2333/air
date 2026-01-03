# OS 内核启动代码
.section .text
.global _start
.global kernel_entry

_start:
    # 设置栈指针
    ldr sp, =_stack_top

    # 跳转到内核入口
    b kernel_entry

# 内核入口点
kernel_entry:
    # 保存上下文
    push {r0-r12, lr}

    # 初始化内核
    bl kernel_init

    # 启用中断
    bl enable_interrupts

    # 进入主循环
    bl kernel_main

    # 永不返回
    b .

# 内核初始化
kernel_init:
    push {lr}

    # 初始化内存管理
    bl mm_init

    # 初始化中断控制器
    bl intc_init

    # 初始化定时器
    bl timer_init

    # 初始化调度器
    bl scheduler_init

    pop {lr}
    bx lr

# 启用中断
enable_interrupts:
    push {lr}

    # 设置 CPSR 启用 IRQ
    mrs r0, cpsr
    bic r0, r0, #0x80
    msr cpsr_c, r0

    pop {lr}
    bx lr

# 内核主循环
kernel_main:
    push {lr}

    # 调度任务
    bl schedule

    # 检查中断
    bl check_interrupts

    # 继续循环
    b kernel_main

    pop {lr}
    bx lr

# 栈空间
.section .bss
.align 4
_stack_bottom:
    .space 0x4000
_stack_top:
