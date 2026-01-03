{
  "version": "1.0",
  "units": [
    {
      "id": "u1",
      "path": "boot.S",
      "language": "asm",
      "type": "source",
      "module": "boot",
      "role": "entry",
      "symbols": [
        {
          "name": "_start",
          "kind": "func",
          "entry": true,
          "attrs": {
            "type": "function",
            "visibility": "global"
          }
        },
        {
          "name": "kernel_entry",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "global"
          }
        },
        {
          "name": "kernel_init",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "global"
          }
        },
        {
          "name": "enable_interrupts",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "global"
          }
        },
        {
          "name": "kernel_main",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "global"
          }
        }
      ]
    },
    {
      "id": "u2",
      "path": "mm.h",
      "language": "c",
      "type": "header",
      "module": "mm",
      "role": "module",
      "symbols": [
        {
          "name": "mm_init",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "kmalloc",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "kfree",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "init_page_tables",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "map_page",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        }
      ]
    },
    {
      "id": "u3",
      "path": "mm.c",
      "language": "c",
      "type": "source",
      "module": "mm",
      "role": "module",
      "symbols": [
        {
          "name": "memory_block_t",
          "kind": "struct",
          "entry": false,
          "attrs": {
            "type": "struct",
            "visibility": "private"
          }
        },
        {
          "name": "page_table_entry_t",
          "kind": "struct",
          "entry": false,
          "attrs": {
            "type": "struct",
            "visibility": "private"
          }
        }
      ]
    },
    {
      "id": "u4",
      "path": "scheduler.h",
      "language": "c",
      "type": "header",
      "module": "scheduler",
      "role": "module",
      "symbols": [
        {
          "name": "scheduler_init",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "create_task",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "schedule",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "terminate_task",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "block_task",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        },
        {
          "name": "wakeup_task",
          "kind": "func",
          "entry": false,
          "attrs": {
            "type": "function",
            "visibility": "public"
          }
        }
      ]
    },
    {
      "id": "u5",
      "path": "scheduler.c",
      "language": "c",
      "type": "source",
      "module": "scheduler",
      "role": "module",
      "symbols": [
        {
          "name": "task_t",
          "kind": "struct",
          "entry": false,
          "attrs": {
            "type": "struct",
            "visibility": "private"
          }
        },
        {
          "name": "task_state_t",
          "kind": "enum",
          "entry": false,
          "attrs": {
            "type": "enum",
            "visibility": "public"
          }
        }
      ]
    }
  ]
}
