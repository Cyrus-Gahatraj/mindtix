// HTML pieces shared by the pages: note rows, bars, columns, donut, IQ curve.
import { Marked } from "marked";
import { noteUrl } from "./brain.js";

export const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

// Notes are the user's own markdown and answers come from an LLM: raw HTML shows as text, script links go nowhere
const marked = new Marked({
  renderer: { html: t => esc(typeof t === "string" ? t : t.text) },
  walkTokens: t => { if ((t.type === "link" || t.type === "image") && /^\s*(javascript|vbscript|data:(?!image\/(png|jpe?g|gif|webp)))/i.test(t.href)) t.href = "#" },
});
export const md = s => marked.parse(s);

export function ago(ts) {
  const s = Date.now() / 1000 - ts;
  if (s < 3600) return "just now";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  if (s < 172800) return "yesterday";
  if (s < 604800) return Math.floor(s / 86400) + "d ago";
  return new Date(ts * 1000).toLocaleDateString(undefined, { day: "numeric", month: "short" });
}
export const title = s => s[0].toUpperCase() + s.slice(1);

// Every folder has its own colour, --c0 … --c7 (fixed for the usual folders, hashed for the rest)
const FOLDER = { projects: 0, knowledge: 1, learning: 2, hobbies: 3, self: 4, insight: 5, extra: 6, raw: 7 };
export const fcIndex = f => FOLDER[f] ?? [...String(f)].reduce((h, c) => h + c.charCodeAt(0), 0) % 8;
export const fc = f => `var(--c${fcIndex(f)})`;
export const sum = (list, k) => list.reduce((s, n) => s + n[k], 0);
const shade = i => Math.max(.18, 1 - i * .16);

/** A list of notes; data-* lets the Notes page filter and sort it in the browser. */
export const rows = (list, showFolder) => list.length ? `<div class="list">${list.map(n => `<a class="item" href="${noteUrl(n.id)}" style="--c:${fc(n.folder)}" data-folder="${esc(n.folder)}" data-title="${esc(n.title.toLowerCase())}" data-mod="${n.mod}"><span class="t">${esc(n.title)}</span>${n.excerpt ? `<span class="x">${esc(n.excerpt)}</span>` : ""}<span class="d">${showFolder ? `<span class="tagf">#${esc(n.folder)}</span> · ` : ""}${ago(n.mod)}</span></a>`).join("")}</div>` : `<p class="empty-note">nothing here yet</p>`;
export const bars = list => `<div class="bars">${list.map(b => `<div class="bar"${b.c ? ` style="--c:${b.c}"` : ""} title="${esc(b.label)}: ${esc(b.text)}"><span class="l2">${esc(b.label)}</span><span class="track"><span class="fill" style="width:${b.value / b.max * 100}%"></span></span><span class="val">${esc(b.text)}</span></div>`).join("")}</div>`;
export const testBars = (t, order) => order.filter(k => t?.scores?.[k] != null).map(k => ({ label: k, value: t.scores[k], max: 100, text: String(t.scores[k]) }));
export const stats = list => `<div class="stats">${list.map(([v, l, x]) => `<div><span class="v">${esc(v)}</span><span class="label">${esc(l)}</span>${x ? `<span class="muted" style="font-size:14px">${esc(x)}</span>` : ""}</div>`).join("")}</div>`;
export const noteBars = (list, val, text) => list.map(n => ({ label: n.title, value: val(n), text: text(n) }))
  .sort((a, b) => b.value - a.value).slice(0, 8).map((b, _, all) => ({ ...b, max: all[0].value || 1 }));

/** Column chart: [{label, value}] as HTML bars, for counts over time or per box. */
export function columns(list, what) {
  const max = Math.max(1, ...list.map(c => c.value));
  return `<div class="colchart${list.length > 8 ? " dense" : ""}" role="img" aria-label="${esc(what)}">` + list.map(c =>
    `<div class="col" title="${esc(c.label)}: ${c.value} ${esc(what)}"><span class="top">${c.value ? `<span>${c.value}</span>` : ""}<span class="b" style="height:${c.value / max * 80}%"></span></span><span class="l">${esc(c.label)}</span></div>`
  ).join("") + `</div>`;
}

/** Notes touched per week over the last `weeks` weeks, oldest first (by file modified time). */
export function activity(list, weeks = 12) {
  const now = Date.now() / 1000, cols = Array.from({ length: weeks }, (_, i) => ({
    label: new Date((now - (weeks - 1 - i) * 604800) * 1000).toLocaleDateString(undefined, { day: "numeric", month: "short" }), value: 0 }));
  for (const n of list) { const w = Math.floor((now - n.mod) / 604800); if (w >= 0 && w < weeks) cols[weeks - 1 - w].value++ }
  return columns(cols, "notes touched");
}

/** Donut: [{label, value, href}] as share of the total, with a legend. */
export function donut(list, unit) {
  const total = list.reduce((s, c) => s + c.value, 0) || 1, C = 2 * Math.PI * 46;
  let at = 0;
  const rings = list.map((c, i) => {
    const len = c.value / total * C, ring = `<circle cx="60" cy="60" r="46" fill="none" stroke="${c.c || "var(--fg)"}" stroke-width="16" opacity="${c.c ? 1 : shade(i)}" stroke-dasharray="${len} ${C}" stroke-dashoffset="${-at}" transform="rotate(-90 60 60)"><title>${esc(c.label)}: ${c.value} ${unit}</title></circle>`;
    at += len;
    return ring;
  }).join("");
  return `<div class="donut"><svg viewBox="0 0 120 120" role="img" aria-label="${esc(unit)} by folder">${rings}<text x="60" y="58" text-anchor="middle" style="font-size:18px;fill:var(--fg)">${total}</text><text x="60" y="74" text-anchor="middle">${esc(unit)}</text></svg>` +
    `<div class="legend">${list.map((c, i) => `<a href="${c.href || "#"}"><i style="${c.c ? `--c:${c.c}` : `opacity:${shade(i)}`}"></i><span>${esc(c.label)}</span><span>${c.value} · ${Math.round(c.value / total * 100)}%</span></a>`).join("")}</div></div>`;
}

export const byFolder = (D, k) => D.folders.map(f => {
  const list = D.notes.filter(n => n.folder === f);
  return { label: f, value: k === "notes" ? list.length : sum(list, k), href: "/notes?f=" + encodeURIComponent(f), c: fc(f) };
}).sort((a, b) => b.value - a.value);

/** IQ normal curve (mean 100, sd 15) over 55..145 with the estimated band shaded. */
export function bell(low, high) {
  const px = iq => (iq - 55) / 90 * 600, py = iq => 110 - Math.exp(-(((iq - 100) / 15) ** 2) / 2) * 100;
  let c = "", b = `M${px(low)} 110 `;
  for (let iq = 55; iq <= 145; iq++) c += `${iq === 55 ? "M" : "L"}${px(iq).toFixed(1)} ${py(iq).toFixed(1)} `;
  for (let iq = low; iq <= high; iq++) b += `L${px(iq).toFixed(1)} ${py(iq).toFixed(1)} `;
  return `<svg viewBox="0 0 600 130" width="100%" role="img" aria-label="Estimated IQ range ${low} to ${high} on a normal curve">
    <path d="${b}L${px(high)} 110 Z" fill="var(--fg)" opacity=".14"></path><path d="${c}" fill="none" stroke="var(--muted)" stroke-width="1.5"></path>
    <line x1="0" x2="600" y1="110" y2="110" stroke="var(--line)"></line><text x="300" y="125" text-anchor="middle">100</text>
    <text x="${px(low)}" y="125" text-anchor="middle">${low}</text><text x="${px(high)}" y="125" text-anchor="middle">${high}</text></svg>`;
}

/** An Ask answer as HTML: [[wikilinks]] to notes become links. */
export const answerHtml = (D, text) => md(D.linkify(text));
