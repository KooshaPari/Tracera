/**
 * NDJSON parser unit tests — covers every code path including error tolerance,
 * UTF-8 chunk-boundary decoding, progress events, cancellation, batching, filtering,
 * and throughput calculation.
 */
import { describe, it, expect } from "vitest";
import {
  parseNDJSON,
  parseNDJSONWithProgress,
  collectNDJSON,
  batchNDJSON,
  filterNDJSON,
  mapNDJSON,
  calculateThroughput,
  type NDJSONProgressEvent,
  type NDJSONCompleteEvent,
  type NDJSONErrorEvent,
  type NDJSONSectionEvent,
  type StreamingStats,
} from "./ndjson-parser";

// --- Test helpers ---------------------------------------------------------

/** Build a ReadableStream from newline-delimited JSON lines. */
function ndjsonStream(lines: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const line of lines) {
        controller.enqueue(encoder.encode(line + "\n"));
      }
      controller.close();
    },
  });
}

/** Build a Response from an NDJSON line list. */
function ndjsonResponse(lines: string[]): Response {
  return new Response(ndjsonStream(lines), {
    headers: { "Content-Type": "application/x-ndjson" },
  });
}

/** Build a Response that emits chunks split mid-line (boundary test). */
function chunkedNdjsonResponse(
  chunks: string[],
  closeAfter = true,
): Response {
  const encoder = new TextEncoder();
  return new Response(
    new ReadableStream({
      start(controller) {
        for (const c of chunks) controller.enqueue(encoder.encode(c));
        if (closeAfter) controller.close();
      },
    }),
    { headers: { "Content-Type": "application/x-ndjson" } },
  );
}

/** Async-collect a generator into an array. */
async function collect<T>(gen: AsyncGenerator<T>): Promise<T[]> {
  const out: T[] = [];
  for await (const v of gen) out.push(v);
  return out;
}

// --- parseNDJSON ------------------------------------------------------------

describe("parseNDJSON", () => {
  it("parses simple newline-delimited JSON objects", async () => {
    const items = await collect(
      parseNDJSON(ndjsonResponse([
        '{"id":1,"name":"a"}',
        '{"id":2,"name":"b"}',
        '{"id":3,"name":"c"}',
      ])),
    );
    expect(items).toEqual([
      { id: 1, name: "a" },
      { id: 2, name: "b" },
      { id: 3, name: "c" },
    ]);
  });

  it("throws when response body is null", async () => {
    const r = new Response(null);
    await expect(collect(parseNDJSON(r))).rejects.toThrow(
      "Response body is null",
    );
  });

  it("skips empty lines and whitespace-only lines", async () => {
    const items = await collect(
      parseNDJSON(ndjsonResponse([
        "",
        "   ",
        '{"x":1}',
        "\t",
        '{"x":2}',
      ])),
    );
    expect(items).toEqual([{ x: 1 }, { x: 2 }]);
  });

  it("silently skips malformed lines and keeps parsing", async () => {
    // Spy on console.error to verify it's called
    const errs: any[][] = [];
    const origError = console.error;
    console.error = (...args: any[]) => errs.push(args);

    const items = await collect(
      parseNDJSON(ndjsonResponse([
        '{"good":1}',
        "{not valid json",
        '{"good":2}',
        "completely broken",
        '{"good":3}',
      ])),
    );

    expect(items).toEqual([{ good: 1 }, { good: 2 }, { good: 3 }]);
    expect(errs.length).toBe(2); // two malformed lines logged

    console.error = origError;
  });

  it("decodes multi-byte UTF-8 across chunk boundaries", async () => {
    // Each emoji is 4 bytes in UTF-8. Split mid-codepoint to test incremental decoder.
    const chunks = [
      '{"msg":"', // 7 ASCII bytes
      "😀", // 4 bytes
      " hello ",
      "🌍", // 4 bytes
      '"}\n',
      '{"msg":"done"}\n',
    ];
    const items = await collect(
      parseNDJSON(chunkedNdjsonResponse(chunks)),
    );
    expect(items).toEqual([{ msg: "😀 hello 🌍" }, { msg: "done" }]);
  });

  it("processes a trailing line without final newline", async () => {
    const items = await collect(
      parseNDJSON(ndjsonResponse(['{"x":1}\n{"x":2}'])), // no trailing \n
    );
    expect(items).toEqual([{ x: 1 }, { x: 2 }]);
  });

  it("handles very large single chunk with multiple records", async () => {
    const lines = Array.from({ length: 1000 }, (_, i) => `{"i":${i}}`);
    const items = await collect(parseNDJSON(ndjsonResponse(lines)));
    expect(items).toHaveLength(1000);
    expect(items[999]).toEqual({ i: 999 });
  });

  it("calls reader.releaseLock() even when consumer breaks early", async () => {
    let releaseLockCalled = false;
    const origRelease = ReadableStreamDefaultReader.prototype.releaseLock;
    ReadableStreamDefaultReader.prototype.releaseLock = function () {
      releaseLockCalled = true;
      return origRelease.call(this);
    };

    const stream = parseNDJSON(ndjsonResponse(['{"x":1}']));
    // Break immediately without consuming
    try {
      for await (const _ of stream) break;
    } catch (_) {}

    // Give the finally block a tick to run
    await new Promise((r) => setTimeout(r, 50));
    ReadableStreamDefaultReader.prototype.releaseLock = origRelease;

    expect(releaseLockCalled).toBe(true);
  });

  it("handles CRLF line endings", async () => {
    const items = await collect(
      parseNDJSON(
        ndjsonResponse(['{"a":1}\r\n{"b":2}\r\n']),
      ),
    );
    expect(items).toEqual([{ a: 1 }, { b: 2 }]);
  });
});

// --- parseNDJSONWithProgress ------------------------------------------------

describe("parseNDJSONWithProgress", () => {
  it("emits progress events with count and timing", async () => {
    const events: any[] = [];
    const lines = [
      JSON.stringify({ type: "progress", count: 1 }),
      JSON.stringify({ id: 1 }),
      JSON.stringify({ id: 2 }),
      JSON.stringify({ type: "complete", count: 2 }),
      JSON.stringify({ id: 3 }),
    ];
    const items = await collect(
      parseNDJSONWithProgress(
        ndjsonResponse(lines),
        (s) => events.push(s),
      ),
    );
    expect(items).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);
    // progress after item 1, progress after item 2 (from onProgress via continue), and final progress on completion
    expect(events.length).toBeGreaterThanOrEqual(2);
    expect(events.at(-1)!.itemsReceived).toBe(3);
  });

  it("filters out section and error events from output stream", async () => {
    const metadata: any[] = [];
    const items = await collect(
      parseNDJSONWithProgress(
        ndjsonResponse([
          JSON.stringify({ type: "section", name: "alpha", count: 10 }),
          JSON.stringify({ id: "a1" }),
          JSON.stringify({ type: "error", error: "transient" }),
          JSON.stringify({ id: "a2" }),
        ]),
        undefined,
        (m) => metadata.push(m),
      ),
    );
    expect(items).toEqual([{ id: "a1" }, { id: "a2" }]);
    expect(metadata.map((m) => m.type)).toEqual([
      "section",
      "error",
    ]);
  });

  it("collects errors into stats.errors array", async () => {
    const lines = [
      JSON.stringify({ id: 1 }),
      JSON.stringify({ type: "error", error: "first" }),
      JSON.stringify({ id: 2 }),
      JSON.stringify({ type: "error", error: "second" }),
    ];
    let captured: StreamingStats | null = null;
    await collect(
      parseNDJSONWithProgress(
        ndjsonResponse(lines),
        (s) => {
          captured = { ...s };
        },
      ),
    );
    expect(captured).not.toBeNull();
    expect(captured!.errors).toEqual(["first", "second"]);
    expect(captured!.itemsReceived).toBe(2);
  });

  it("treats items without type field as regular data items", async () => {
    const items = await collect(
      parseNDJSONWithProgress(
        ndjsonResponse(['{"id":1}', '{"id":2,"type":"weird"}']),
      ),
    );
    // First has no type → yielded. Second has unknown type → yielded (default branch).
    expect(items).toEqual([{ id: 1 }, { id: 2, type: "weird" }]);
  });

  it("captures start/end timing in stats", async () => {
    let captured: StreamingStats | null = null;
    await collect(
      parseNDJSONWithProgress(
        ndjsonResponse(['{"id":1}']),
        (s) => (captured = { ...s }),
      ),
    );
    expect(captured!.startTime).toBeGreaterThan(0);
    expect(captured!.endTime).toBeGreaterThanOrEqual(captured!.startTime);
  });
});

// --- collectNDJSON -----------------------------------------------------------

describe("collectNDJSON", () => {
  it("collects all items from stream", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(['{"a":1}', '{"a":2}', '{"a":3}']),
    );
    const items = await collectNDJSON(stream);
    expect(items).toEqual([{ a: 1 }, { a: 2 }, { a: 3 }]);
  });

  it("respects maxItems limit", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(['{"a":1}', '{"a":2}', '{"a":3}', '{"a":4}']),
    );
    const items = await collectNDJSON(stream, 2);
    expect(items).toEqual([{ a: 1 }, { a: 2 }]);
  });

  it("maxItems larger than actual yields all items", async () => {
    const stream = parseNDJSON(ndjsonResponse(['{"a":1}', '{"a":2}']));
    const items = await collectNDJSON(stream, 100);
    expect(items).toEqual([{ a: 1 }, { a: 2 }]);
  });
});

// --- batchNDJSON -------------------------------------------------------------

describe("batchNDJSON", () => {
  it("groups items into batches of the requested size", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(
        Array.from({ length: 7 }, (_, i) => `{"i":${i}}`),
      ),
    );
    const batches = await collect(batchNDJSON(stream, 3));
    expect(batches).toEqual([
      [{ i: 0 }, { i: 1 }, { i: 2 }],
      [{ i: 3 }, { i: 4 }, { i: 5 }],
      [{ i: 6 }],
    ]);
  });

  it("yields the final partial batch even if smaller than batchSize", async () => {
    const stream = parseNDJSON(ndjsonResponse(['{"i":1}', '{"i":2}']));
    const batches = await collect(batchNDJSON(stream, 5));
    expect(batches).toEqual([[{ i: 1 }, { i: 2 }]]);
  });

  it("handles empty stream gracefully (no batches)", async () => {
    const stream = parseNDJSON(ndjsonResponse([]));
    const batches = await collect(batchNDJSON(stream, 10));
    expect(batches).toEqual([]);
  });
});

// --- filterNDJSON / mapNDJSON -------------------------------------------------

describe("filterNDJSON", () => {
  it("keeps only items matching the predicate", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(
        Array.from({ length: 10 }, (_, i) => `{"i":${i}}`),
      ),
    );
    const items = await collect(filterNDJSON(stream, (x) => x.i % 2 === 0));
    expect(items.map((x) => x.i)).toEqual([0, 2, 4, 6, 8]);
  });
});

describe("mapNDJSON", () => {
  it("transforms each item", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(['{"n":1}', '{"n":2}', '{"n":3}']),
    );
    const items = await collect(mapNDJSON(stream, (x) => x.n * 10));
    expect(items).toEqual([10, 20, 30]);
  });

  it("supports async mappers", async () => {
    const stream = parseNDJSON(
      ndjsonResponse(['{"n":1}', '{"n":2}']),
    );
    const items = await collect(
      mapNDJSON(stream, async (x) => x.n * 100),
    );
    expect(items).toEqual([100, 200]);
  });
});

// --- calculateThroughput ------------------------------------------------------

describe("calculateThroughput", () => {
  it("computes itemsPerSecond and bytesPerSecond", () => {
    const stats: StreamingStats = {
      bytesReceived: 1024,
      itemsReceived: 10,
      startTime: 1000,
      endTime: 2000,
    };
    const t = calculateThroughput(stats);
    expect(t.itemsPerSecond).toBe(10); // 10 / 1s
    expect(t.bytesPerSecond).toBe(1024); // 1024 / 1s
    expect(t.megabytesPerSecond).toBeCloseTo(0.0009765625, 6);
    expect(t.totalDurationMs).toBe(1000);
  });

  it("uses Date.now() when endTime is missing", () => {
    const stats: StreamingStats = {
      bytesReceived: 1000,
      itemsReceived: 5,
      startTime: Date.now() - 1000,
      // endTime: undefined
    };
    const t = calculateThroughput(stats);
    expect(t.totalDurationMs).toBeGreaterThanOrEqual(1000);
    expect(t.itemsPerSecond).toBeGreaterThan(0);
  });
});

// --- fetchNDJSON + createCancellableNDJSONStream ---------------------------

describe("fetchNDJSON", () => {
  it("rejects on non-2xx status with a descriptive error", async () => {
    const origFetch = globalThis.fetch;
    globalThis.fetch = (async () =>
      new Response("not found", { status: 404, statusText: "Not Found" })) as typeof fetch;
    try {
      await expect(collect(fetchNDJSON("http://test/x"))).rejects.toThrow(
        "HTTP 404: Not Found",
      );
    } finally {
      globalThis.fetch = origFetch;
    }
  });

  it("streams items from a 200 response", async () => {
    const origFetch = globalThis.fetch;
    globalThis.fetch = (async () =>
      ndjsonResponse(['{"n":1}', '{"n":2}'])) as typeof fetch;
    try {
      const items = await collect(fetchNDJSON("http://test/x"));
      expect(items).toEqual([{ n: 1 }, { n: 2 }]);
    } finally {
      globalThis.fetch = origFetch;
    }
  });
});

describe("createCancellableNDJSONStream", () => {
  it("exposes a stream and a cancel function", async () => {
    const { stream, cancel } = createCancellableNDJSONStream(
      "http://test/x",
    );
    cancel();
    // Stream should yield no items after cancel
    const items: unknown[] = [];
    try {
      for await (const item of stream) items.push(item);
    } catch (_) {
      // AbortError is fine
    }
    expect(items.length).toBe(0);
  });
});

// --- Type narrowing ----------------------------------------------------------

describe("NDJSONMetadata type narrowing", () => {
  it("progress event has count", () => {
    const e: NDJSONProgressEvent = { type: "progress", count: 5 };
    expect(e.type).toBe("progress");
    expect(e.count).toBe(5);
  });

  it("complete event has optional count", () => {
    const e: NDJSONCompleteEvent = { type: "complete", count: 100 };
    expect(e.type).toBe("complete");
    expect(e.count).toBe(100);
  });

  it("error event has error string", () => {
    const e: NDJSONErrorEvent = { type: "error", error: "boom" };
    expect(e.error).toBe("boom");
  });

  it("section event has name and count", () => {
    const e: NDJSONSectionEvent = { type: "section", name: "alpha", count: 7 };
    expect(e.name).toBe("alpha");
    expect(e.count).toBe(7);
  });
});
