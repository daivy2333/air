// Rust 模块，使用 no_std 以便与其他语言链接
#![no_std]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

// 导出给其他语言调用的函数
#[no_mangle]
pub extern "C" fn rust_calculate_product(a: i32, b: i32) -> i32 {
    a * b
}

#[no_mangle]
pub extern "C" fn rust_print_stats(count: i32, total: i32) {
    // 注意：这里不能直接使用 println!，因为没有 std
    // 实际实现中应该调用 C 的 printf
    let _ = (count, total);
}

// 内部辅助函数
fn internal_divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        0
    } else {
        a / b
    }
}

// 公开的辅助函数
#[no_mangle]
pub extern "C" fn rust_calculate_average(values: *const i32, count: i32) -> i32 {
    if count == 0 {
        return 0;
    }

    let mut sum = 0i32;
    unsafe {
        for i in 0..count {
            sum += *values.add(i as usize);
        }
    }

    internal_divide(sum, count)
}
