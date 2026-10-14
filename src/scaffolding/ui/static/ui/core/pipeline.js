// What every request the page makes goes through, as decorators.
//
// A `send` is `(request, native) => Promise`: it resolves when the request has been
// dealt with. `native` is what the browser would have done without us (submit the
// form, follow the link). A decorator takes a send and returns a send, so what
// must happen around every request is written once, in one place each, and
// `compose` stacks them: the first is the outermost, and each puts its exit under
// its entry (`try`/`finally`), the way an effect rewinds. Browser-free.

/** The request never got an answer: the one failure the browser can safely redo. */
export class Unreached extends Error {}

export const compose = (...decorators) => (send) => decorators.reduceRight((next, wrap) => wrap(next), send);

/** Hand an unanswered request back to the browser. Any other failure is ours to see:
 * a POST the server did answer must not be sent a second time. */
export const fallback = (next) => async (request, native) => {
  try {
    return await next(request, native);
  } catch (error) {
    if (!(error instanceof Unreached)) throw error;
    native();
  }
};

/** One command at a time, and nothing else while it is out: the page is about to
 * change under whatever else was asked, and a second click would be a second goal. */
export const once = (next) => {
  let sending = false;
  return async (request, native) => {
    if (sending) return;
    if (request.method === "GET") return next(request, native);
    sending = true;
    try {
      return await next(request, native);
    } finally {
      sending = false;
    }
  };
};

/** The newest request wins over a read still out: an old answer must not land on a
 * newer page. A command is never aborted - the server may already have it. */
export const latest = (next) => {
  let reading;
  return async (request, native) => {
    reading?.abort();
    reading = undefined;
    if (request.method !== "GET") return next(request, native);
    const mine = new AbortController();
    reading = mine;
    try {
      return await next(new Request(request, { signal: mine.signal }), native);
    } catch (error) {
      if (!mine.signal.aborted) throw error;
    } finally {
      if (reading === mine) reading = undefined;
    }
  };
};
