#[macro_use] extern crate rocket;

use std::sync::Arc
use std::sync::atomic::{AtomicUsize, Ordering};
use rocket::State;

struct HitCount {
    count: Arc<i32>
}

#[get("/")]
fn index( hit_count: &State<HitCount> ) -> String {
    
    // let cur_count = hit_count.count.load(Ordering::Relaxed);
    let new_count = hit_count.count.load(Ordering::Relaxed) + 1;
    hit_count.count. = AtomicUsize::new( new_count );  
    
    format!("Hello, world! {}\n", new_count)
}

#[launch]
fn rocket() -> _ {
    rocket::build()
    .manage(HitCount { count: Arc::new(0)} )
    .mount("/", routes![index])
}
