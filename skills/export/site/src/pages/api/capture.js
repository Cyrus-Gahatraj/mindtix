import { capture, WriteError } from "../../lib/brain.js";

export async function POST({ request }) {
  const { text } = await request.json().catch(() => ({}));
  try {
    return Response.json(capture(text));
  } catch (e) {
    if (e instanceof WriteError) return Response.json({ error: e.message }, { status: e.status });
    throw e;
  }
}
