// Small helpers the page scripts share.
export const $ = id => document.getElementById(id);
export const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
export const noteUrl = id => "/n/" + id.split("/").map(encodeURIComponent).join("/");
export const typing = () => /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;

/** POST JSON to the site's API; throws with the server's message. */
export async function api(path, body, method = "POST") {
  const r = await fetch(path, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}

/** A short message at the bottom of the screen. */
export function toast(text, error = false) {
  document.querySelector(".toast")?.remove();
  const t = Object.assign(document.createElement("div"), { className: "toast" + (error ? " error" : ""), textContent: text });
  t.setAttribute("role", "status");
  document.body.append(t);
  setTimeout(() => t.remove(), error ? 6000 : 2600);
}
