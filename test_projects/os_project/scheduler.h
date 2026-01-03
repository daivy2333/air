#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <stdint.h>

// 任务状态枚举
typedef enum {
    TASK_READY,
    TASK_RUNNING,
    TASK_BLOCKED,
    TASK_TERMINATED
} task_state_t;

// 任务控制块
typedef struct task task_t;

// 调度器函数
void scheduler_init(void);
task_t* create_task(void (*entry)(void), uint32_t priority);
void schedule(void);
void terminate_task(void);
void block_task(void);
void wakeup_task(task_t* task);

// 常量
#define MAX_TASKS 16
#define STACK_SIZE 4096

#endif
