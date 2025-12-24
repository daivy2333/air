<pir>
<meta>
name: rust_learn
root: /home/daivy/projects/pad/rust_learn
profile: generic
lang: Rust
</meta>
<units>
u0: hello_package/src/lib.rs type=Rust role=lib module=src
u1: hello_package/src/main.rs type=Rust role=lib module=src
u2: hello_package/src/back_of_house.rs type=Rust role=lib module=src
u3: hello_package/src/front_of_house/serving.rs type=Rust role=lib module=front_of_house
u4: hello_package/src/front_of_house/hosting.rs type=Rust role=lib module=front_of_house
u5: hello_package/src/front_of_house/mod.rs type=Rust role=lib module=front_of_house
u6: make_out/src/main.rs type=Rust role=lib module=src
u7: a_find/src/main.rs type=Rust role=lib module=src
u8: algor_learn/src/bucket_sort.rs type=Rust role=lib module=src
u9: algor_learn/src/main.rs type=Rust role=lib module=src
u10: algor_learn/src/cocktail_shaker_sort.rs type=Rust role=lib module=src
u11: algor_learn/src/bubble_sort.rs type=Rust role=lib module=src
u12: adder/src/lib.rs type=Rust role=lib module=src
u13: variables/src/main.rs type=Rust role=lib module=src
u14: hello_world/src/main.rs type=Rust role=lib module=src
u15: minigrep/src/lib.rs type=Rust role=lib module=src
u16: minigrep/src/main.rs type=Rust role=lib module=src
</units>
<dependency-pool>
d0: use:[hello_package::back_of_house]
d1: use:[hello_package::eat_at_restaurant]
d2: use:[hello_package::front_of_house]
d3: use:[minigrep::Config]
d4: use:[rand::Rng]
d5: use:[stdlib:rust]
d6: use:[super::*]
</dependency-pool>
<dependencies>
u1->refs:[d1 d2 d0]
u6->refs:[d5]
u7->refs:[d5]
u14->refs:[d5 d4]
u15->refs:[d5 d6]
u16->refs:[d5 d3]
</dependencies>
<symbols>
eat_at_restaurant:u0 func
main:u1 func entry=true
fix_incorrect_order:u2 func
cook_order:u2 func
take_order:u3 func
serve_order:u3 func
take_payment:u3 func
note_complain:u3 func
complain:u3 func
add_to_waitlist:u4 func
seat_at_table:u4 func
main:u6 func entry=true
initialize_knowledge_base:u6 func
get_user_facts:u6 func
run_inference:u6 func
display_results:u6 func
Rule:u6 struct
cmp:u7 func
partial_cmp:u7 func
main:u7 func entry=true
heuristic:u7 func
reconstruct_path:u7 func
Node:u7 struct
bucket_sort:u8 func
main:u9 func entry=true
cocktail_shaker_sort:u10 func
bubble_sort:u11 func
it_works:u12 func
largest:u13 func
main:u13 func entry=true
main:u14 func entry=true
build:u15 func
run:u15 func
case_sensitive:u15 func
case_insensitive:u15 func
one_result:u15 func
search:u15 func
search:u15 func
search_case_insensitive:u15 func
Config:u15 struct
main:u16 func entry=true
run:u16 func
new:u16 func
build:u16 func
Config:u16 struct
</symbols>
</pir>