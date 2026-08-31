#![no_main]
use libfuzzer_sys::fuzz_target;
use std::str::from_utf8;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = from_utf8(data) {
        // Simulate list parameter parsing
        let _ = parse_list_params(s);
    }
});

fn parse_list_params(s: &str) -> Result<(), ()> {
    // Placeholder for actual parsing logic
    let _ = s.split(',').collect::<Vec<_>>();
    Ok(())
}
