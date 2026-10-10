import { saveLLM } from "../../lib/ask.js";

export async function POST({ request }) {
  try {
    return Response.json(saveLLM(await request.json().catch(() => ({}))));
  } catch (e) {
    return Response.json({ error: e.message }, { status: 400 });
  }
}
