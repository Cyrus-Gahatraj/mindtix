import fs from "node:fs";
import path from "node:path";
import { IMAGES, shown, walk } from "../../lib/brain.js";

// Images that notes embed, only from folders the site shows (never private/, logs/, raw/imports/)
export function GET({ params }) {
  const type = IMAGES[path.extname(params.path || "").toLowerCase()];
  const hit = type && shown(params.path) && walk().find(([rel]) => rel === params.path);
  if (!hit) return new Response("not found", { status: 404 });
  return new Response(fs.readFileSync(hit[1]), { headers: { "Content-Type": type, "Cache-Control": "no-store", "Content-Security-Policy": "sandbox" } });
}
