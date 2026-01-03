// 任务调度器

#include <stdint.h>

#define MAX_TASKS 16
#define STACK_SIZE 4096

// 任务状态
typedef enum {
    TASK_READY,
    TASK_RUNNING,
    TASK_BLOCKED,
    TASK_TERMINATED
} task_state_t;

// 任务控制块
typedef struct task {
    uint32_t id;
    task_state_t state;
    uint32_t priority;
    uint32_t* stack;
    uint32_t stack_pointer;
    uint32_t* context;
    struct task* next;
} task_t;

// 调度器状态
static task_t* current_task = NULL;
static task_t* task_queue = NULL;
static uint32_t next_task_id = 0;

// 初始化调度器
void scheduler_init(void) {
    current_task = NULL;
    task_queue = NULL;
    next_task_id = 0;
}

// 创建新任务
task_t* create_task(void (*entry)(void), uint32_t priority) {
    // 分配任务结构
    task_t* task = (task_t*)kmalloc(sizeof(task_t));
    if (task == NULL) {
        return NULL;
    }

    // 分配栈空间
    task->stack = (uint32_t*)kmalloc(STACK_SIZE);
    if (task->stack == NULL) {
        kfree(task);
        return NULL;
    }

    // 初始化任务
    task->id = next_task_id++;
    task->state = TASK_READY;
    task->priority = priority;
    task->stack_pointer = (uint32_t)task->stack + STACK_SIZE - 16;
    task->context = NULL;
    task->next = NULL;

    // 设置初始上下文
    task->stack[STACK_SIZE/4 - 1] = (uint32_t)entry;  // 返回地址

    // 添加到队列
    if (task_queue == NULL) {
        task_queue = task;
    } else {
        task_t* last = task_queue;
        while (last->next != NULL) {
            last = last->next;
        }
        last->next = task;
    }

    return task;
}

// 调度下一个任务
void schedule(void) {
    if (task_queue == NULL) {
        return;
    }

    // 保存当前任务上下文
    if (current_task != NULL && current_task->state == TASK_RUNNING) {
        current_task->state = TASK_READY;
        // 保存寄存器上下文
    }

    // 选择下一个任务
    task_t* next = task_queue;
    task_t* highest = NULL;
    uint32_t highest_priority = 0;

    while (next != NULL) {
        if (next->state == TASK_READY && 
            (highest == NULL || next->priority > highest_priority)) {
            highest = next;
            highest_priority = next->priority;
        }
        next = next->next;
    }

    if (highest != NULL) {
        current_task = highest;
        current_task->state = TASK_RUNNING;
        // 恢复寄存器上下文
        // 切换到新任务的栈
    }
}

// 终止当前任务
void terminate_task(void) {
    if (current_task != NULL) {
        current_task->state = TASK_TERMINATED;
        schedule();  // 切换到其他任务
    }
}

// 阻塞当前任务
void block_task(void) {
    if (current_task != NULL) {
        current_task->state = TASK_BLOCKED;
        schedule();  // 切换到其他任务
    }
}

// 唤醒任务
void wakeup_task(task_t* task) {
    if (task != NULL) {
        task->state = TASK_READY;
    }
}
