import { grade, RATINGS, WriteError } from "../../lib/brain.js";

export async function POST({ request }) {
  const { topic, question, rating, sure = null } = await request.json().catch(() => ({}));
  if (typeof topic !== "string" || typeof question !== "string" || !RATINGS.includes(rating) || ![true, false, null].includes(sure))
    return Response.json({ error: "need topic, question, rating (again, hard, good or easy) and sure (true, false or null)" }, { status: 400 });
  try {
    return Response.json(grade(topic, question, rating, sure));
  } catch (e) {
    if (e instanceof WriteError) return Response.json({ error: e.message }, { status: e.status });
    throw e;
  }
}
