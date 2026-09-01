#![no_main]
use libfuzzer_sys::fuzz_target;
use std::str::from_utf8;

fuzz_target!(|data: &[u8]| {
    if let Ok(s) = from_utf8(data) {
        // Simulate parsing OpenTelemetry payload
        let _ = parse_otel_payload(s);
    }
});

fn parse_otel_payload(s: &str) -> Result<(), ()> {
    // Placeholder for actual parsing logic
    if s.is_empty() {
        return Err(());
    }
    Ok(())
}
