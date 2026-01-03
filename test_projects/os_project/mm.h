#ifndef MM_H
#define MM_H

#include <stdint.h>

// 内存管理函数
void mm_init(void);
void* kmalloc(uint32_t size);
void kfree(void* ptr);
void init_page_tables(void);
void map_page(uint32_t virt, uint32_t phys, uint32_t flags);

// 常量定义
#define PAGE_SIZE 4096
#define HEAP_SIZE (1024 * 1024)

#endif
