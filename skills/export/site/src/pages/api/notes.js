import { saveNote, WriteError } from "../../lib/brain.js";

export async function POST({ request }) {
  const { id, md, mod } = await request.json().catch(() => ({}));
  if (typeof md !== "string") return Response.json({ error: "need the note's markdown" }, { status: 400 });
  try {
    return Response.json(saveNote(id, md, typeof mod === "number" ? mod : null));
  } catch (e) {
    if (e instanceof WriteError) return Response.json({ error: e.message }, { status: e.status });
    throw e;
  }
}
