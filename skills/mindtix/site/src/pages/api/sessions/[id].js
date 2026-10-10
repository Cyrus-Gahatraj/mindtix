import { deleteSession, hasSession, readLog } from "../../../lib/ask.js";

export const GET = ({ params }) => hasSession(params.id) ? Response.json(readLog(params.id)) : Response.json({ error: "not found" }, { status: 404 });
export const DELETE = ({ params }) => deleteSession(params.id) ? Response.json({ ok: true }) : Response.json({ error: "not found" }, { status: 404 });
