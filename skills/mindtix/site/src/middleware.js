import { BRAIN, isBrain } from "./lib/brain.js";

// The site reads and writes your brain, so it only answers to this machine: the Host must be
// local (no DNS rebinding) and API writes must be JSON (a cross-site form can't send that).
export function onRequest({ request, url }, next) {
  if (!["127.0.0.1", "localhost", "[::1]"].includes(url.hostname) || !/^(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$/.test(request.headers.get("host") || ""))
    return new Response("mindtix only serves 127.0.0.1", { status: 403 });
  if (request.method !== "GET" && request.method !== "HEAD" && !(request.headers.get("content-type") || "").startsWith("application/json"))
    return Response.json({ error: "send JSON" }, { status: 415 });
  if (!isBrain()) return new Response(`${BRAIN} is not a mindtix brain (no MIND.md). Set MINDTIX_BRAIN to the brain's folder.`, { status: 500 });
  // Old addresses from earlier versions of the site
  const old = url.pathname.match(/^\/(all|stats|f\/([^/]+))\/?$/);
  if (old) return Response.redirect(new URL(old[1] === "stats" ? "/insight" : old[2] ? "/notes?f=" + old[2] : "/notes", url), 301);
  return next();
}
