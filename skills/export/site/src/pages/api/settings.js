import { brainFolders, saveSettings } from "../../lib/brain.js";
import { MODELS } from "../../lib/ask.js";

// Settings → mindtix.json. Only known keys and values get through.
export async function POST({ request }) {
  const b = await request.json().catch(() => ({})), patch = {};
  if ("engine" in b) {
    if (!["", "claude", "api"].includes(b.engine)) return Response.json({ error: "Unknown engine." }, { status: 400 });
    patch.engine = b.engine;
  }
  if ("model" in b) {
    if (!["", ...MODELS].includes(b.model)) return Response.json({ error: "Unknown model." }, { status: 400 });
    patch.model = b.model;
  }
  if ("edits" in b) patch.edits = b.edits !== false;
  if ("folders" in b) {
    const all = brainFolders(), list = String(b.folders).split(/\s+/).filter(Boolean);
    if (b.folders !== "all" && (!list.length || list.some(f => !all.includes(f)))) return Response.json({ error: "Unknown folder." }, { status: 400 });
    patch.folders = b.folders === "all" ? "all" : list.join(" ");
  }
  return Response.json(saveSettings(patch));
}
