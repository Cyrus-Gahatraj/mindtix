import { load } from "../../lib/brain.js";
import { md } from "../../lib/ui.js";

export async function POST({ request }) {
  const body = await request.json().catch(() => ({}));
  return Response.json({ html: md(load().linkify(String(body.md || ""))) });
}
