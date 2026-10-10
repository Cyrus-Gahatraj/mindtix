import { removePhoto, savePhoto, WriteError } from "../../lib/brain.js";

export async function POST({ request }) {
  const { data } = await request.json().catch(() => ({}));
  try {
    return Response.json(savePhoto(data));
  } catch (e) {
    if (e instanceof WriteError) return Response.json({ error: e.message }, { status: e.status });
    throw e;
  }
}
export const DELETE = () => Response.json(removePhoto());
