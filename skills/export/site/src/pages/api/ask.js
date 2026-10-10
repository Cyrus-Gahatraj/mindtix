import { load } from "../../lib/brain.js";
import { ask, SESSION } from "../../lib/ask.js";
import { answerHtml } from "../../lib/ui.js";

// One chat turn, streamed as JSON lines: {t: "session"|"text"|"step", v}, then {t: "done", html} or {t: "error", v}.
// Closing the request (the Stop button) stops the engine; what came so far is kept in the log.
export async function POST({ request }) {
  const body = await request.json().catch(() => ({}));
  const question = String(body.question || "").trim(), session = body.session || null;
  if (!question || (session && !SESSION.test(String(session))))
    return Response.json({ error: "need a question (and a valid session id, if any)" }, { status: 400 });
  const stop = new AbortController(), enc = new TextEncoder();
  request.signal?.addEventListener("abort", () => stop.abort());
  const stream = new ReadableStream({
    async start(out) {
      const send = o => { try { out.enqueue(enc.encode(JSON.stringify(o) + "\n")) } catch {} };
      try {
        const r = await ask(session, question, send, stop.signal);
        send({ t: "done", session: r.session, html: answerHtml(load(), r.answer) });
      } catch (e) {
        send({ t: "error", v: e.message });
      }
      try { out.close() } catch {}
    },
    cancel() { stop.abort() },
  });
  return new Response(stream, { headers: { "Content-Type": "application/x-ndjson; charset=utf-8", "Cache-Control": "no-store", "X-Accel-Buffering": "no" } });
}
