import { grade, WriteError } from "../../lib/brain.js";

export async function POST({ request }) {
  const { topic, question, right } = await request.json().catch(() => ({}));
  if (typeof topic !== "string" || typeof question !== "string" || typeof right !== "boolean")
    return Response.json({ error: "need topic, question and right" }, { status: 400 });
  try {
    return Response.json(grade(topic, question, right));
  } catch (e) {
    if (e instanceof WriteError) return Response.json({ error: e.message }, { status: e.status });
    throw e;
  }
}
