import fs from "node:fs";
import path from "node:path";
import { BRAIN, photo, PHOTO_TYPES } from "../lib/brain.js";

// The profile picture (self/photo.*). The page adds ?v=<modified time>, so a new one shows at once.
export function GET() {
  const p = photo();
  if (!p) return new Response("no picture", { status: 404 });
  return new Response(fs.readFileSync(path.join(BRAIN, p)), { headers: {
    "Content-Type": PHOTO_TYPES[path.extname(p).slice(1).toLowerCase()], "Cache-Control": "private, max-age=31536000, immutable", "Content-Security-Policy": "sandbox" } });
}
