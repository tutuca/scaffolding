// Pure tests for `core/pipeline.js`: fake sends, no DOM. Run with `make test-js`.
import { test } from "node:test";
import assert from "node:assert/strict";

import { Unreached, compose, fallback, latest, once } from "../../../src/scaffolding/ui/static/ui/core/pipeline.js";

const get = () => new Request("http://x/planes");
const post = () => new Request("http://x/metas/", { method: "POST", body: "a=1" });
const gate = () => {
  let open;
  const closed = new Promise((resolve) => {
    open = resolve;
  });
  return { closed, open };
};

// A fetch that is still waiting rejects when its signal aborts; so does this.
const waiting = (request, closed) =>
  Promise.race([
    closed,
    new Promise((_, reject) =>
      request.signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError"))),
    ),
  ]);

test("compose puts the first decorator outermost", async () => {
  const seen = [];
  const mark = (name) => (next) => async (request, native) => {
    seen.push(`in ${name}`);
    try {
      return await next(request, native);
    } finally {
      seen.push(`out ${name}`);
    }
  };

  await compose(mark("a"), mark("b"))(async () => seen.push("send"))(get(), () => {});

  assert.deepEqual(seen, ["in a", "in b", "send", "out b", "out a"]);
});

test("fallback hands an unanswered request to the browser and nothing else", async () => {
  let handed = 0;
  const native = () => handed++;

  assert.equal(await fallback(async () => "ok")(get(), native), "ok");
  await fallback(async () => {
    throw new Unreached("offline");
  })(get(), native);
  assert.equal(handed, 1);
  await assert.rejects(
    fallback(async () => {
      throw new RangeError("ours");
    })(get(), native),
    RangeError,
  );
  assert.equal(handed, 1);
});

test("once lets one command through and drops whatever comes while it is out", async () => {
  const { closed, open } = gate();
  const calls = [];
  const send = once(async (request) => {
    calls.push(request.method);
    await closed;
    return "done";
  });

  const first = send(post(), () => {});
  assert.equal(await send(post(), () => {}), undefined);
  assert.equal(await send(get(), () => {}), undefined);
  open();

  assert.equal(await first, "done");
  assert.deepEqual(calls, ["POST"]);
});

test("once is free again after a command, even one that failed", async () => {
  let fail = true;
  const send = once(async () => {
    if (fail) throw new Unreached("offline");
    return "ok";
  });

  await assert.rejects(send(post(), () => {}), Unreached);
  fail = false;

  assert.equal(await send(post(), () => {}), "ok");
});

test("once lets reads overlap", async () => {
  const { closed, open } = gate();
  const send = once(async () => {
    await closed;
    return "read";
  });

  const both = Promise.all([send(get(), () => {}), send(get(), () => {})]);
  open();

  assert.deepEqual(await both, ["read", "read"]);
});

test("latest aborts a read still out when a newer request arrives", async () => {
  const { closed, open } = gate();
  const signals = [];
  const send = latest(async (request) => {
    signals.push(request.signal);
    if (signals.length === 1) {
      await waiting(request, closed);
      return "stale";
    }
    return "fresh";
  });

  const old = send(get(), () => {});
  assert.equal(await send(get(), () => {}), "fresh");
  open();

  assert.equal(await old, undefined);
  assert.equal(signals[0].aborted, true);
  assert.equal(signals[1].aborted, false);
});

test("latest aborts a read for a command and never aborts the command", async () => {
  const { closed, open } = gate();
  let command;
  const send = latest(async (request) => {
    if (request.method === "POST") {
      command = request;
      return "posted";
    }
    await waiting(request, closed);
  });

  const read = send(get(), () => {});
  assert.equal(await send(post(), () => {}), "posted");
  open();
  await read;

  assert.equal(command.signal.aborted, false);
});

test("latest passes on a failure that was not its abort", async () => {
  const send = latest(async () => {
    throw new Unreached("offline");
  });

  await assert.rejects(send(get(), () => {}), Unreached);
  assert.equal(await latest(async () => "ok")(get(), () => {}), "ok");
});
