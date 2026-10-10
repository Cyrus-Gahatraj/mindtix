// Every page: the ⌘K palette (notes and actions), theme, keyboard shortcuts, the top bar's edge.
import { $, esc, noteUrl, typing } from "./util.js";

// Theme: "system" (no attribute), "light" or "dark"; Settings and ⌘K change it
export function setTheme(t) {
  if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
  else delete document.documentElement.dataset.theme;
  try { t === "system" ? localStorage.removeItem("theme") : localStorage.setItem("theme", t) } catch {}
  dispatchEvent(new Event("themechange"));
}
const isDark = () => (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";

// The top bar gets a hairline once the page scrolls
const top = document.querySelector(".top");
const edge = () => top.classList.toggle("scrolled", scrollY > 4);
addEventListener("scroll", edge, { passive: true });
edge();

// ⌘K: actions first, then notes (fetched on first open, as they are now)
const ACTIONS = [
  ["New note", "/write", "plus", "n"],
  ["Ask your brain", "/ask", "chat"],
  ["Today's session (/mindtix today)", "/ask?run=" + encodeURIComponent("/mindtix today"), "spark"],
  ["Start recall", "/recall", "cards"],
  ["Capture a thought", "/#capture", "edit"],
  ["All notes", "/notes", "menu"],
  ["Graph", "/graph", "graph"],
  ["Insight and stats", "/insight", "graph"],
  ["Profile and picture", "/profile", "edit"],
  ["Settings", "/settings", "settings"],
  ["Switch light / dark", () => setTheme(isDark() ? "light" : "dark"), "sun"],
];
const ICONS = {
  plus: '<path d="M12 5v14M5 12h14"/>', chat: '<path d="M20 12a8 8 0 0 1-11.6 7.1L4 20l1-4.2A8 8 0 1 1 20 12Z"/>',
  spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  cards: '<rect x="3" y="6" width="14" height="14" rx="2"/><path d="M7 3h11a3 3 0 0 1 3 3v11"/>',
  edit: '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4Z"/>', menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  graph: '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="8" r="2.5"/><circle cx="9" cy="18" r="2.5"/><path d="m8.3 7.2 7.4.6M7 8.4l1.4 7.2M16.4 10l-5.8 6.2"/>',
  settings: '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/>', note: '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/>',
};
const svg = k => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${ICONS[k]}</svg>`;
const pal = $("palette"), pin = $("pinput"), pres = $("presults");
let notes = null, hits = [], sel = 0;
async function openPalette() {
  pal.classList.add("open"); pin.value = ""; pin.focus();
  notes ||= await fetch("/search.json").then(r => r.json()).catch(() => []);
  search();
}
const closePalette = () => pal.classList.remove("open");
function search() {
  const q = pin.value.trim().toLowerCase(), terms = q.split(/\s+/).filter(Boolean);
  const acts = ACTIONS.filter(([label]) => terms.every(w => label.toLowerCase().includes(w)))
    .map(([label, go, ic, key]) => ({ go, html: `${svg(ic)}<span class="pm"><span class="pt">${esc(label)}</span></span>${key ? `<kbd>${key.toUpperCase()}</kbd>` : ""}` }));
  let found = [];
  if (terms.length) {
    for (const it of notes || []) {
      const t = it.title.toLowerCase(), x = it.text.toLowerCase();
      if (!terms.every(w => t.includes(w) || x.includes(w))) continue;
      let score = t.startsWith(q) ? 20 : 0;
      for (const w of terms) score += (t.includes(w) ? 10 : 0) + Math.min(x.split(w).length - 1, 5);
      const at = Math.max(0, x.indexOf(terms[0]) - 40);
      let snip = (at ? "…" : "") + esc(it.text.slice(at, at + 140));
      for (const w of terms) snip = snip.replace(new RegExp("(" + esc(w).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
      found.push({ go: noteUrl(it.id), score, html: `${svg("note")}<span class="pm"><span class="pt">${esc(it.title)}</span><span class="ps">${snip}</span></span><span class="pp tagf" style="--c:var(--c${it.c})">#${esc(it.folder)}</span>` });
    }
    found = found.sort((a, b) => b.score - a.score).slice(0, 8);
  } else {
    found = [...(notes || [])].sort((a, b) => b.mod - a.mod).slice(0, 5)
      .map(n => ({ go: noteUrl(n.id), html: `${svg("note")}<span class="pm"><span class="pt">${esc(n.title)}</span></span><span class="pp tagf" style="--c:var(--c${n.c})">#${esc(n.folder)}</span>` }));
  }
  const shownActs = terms.length ? acts.slice(0, 4) : acts.slice(0, 5);
  hits = [...shownActs, ...found];
  pres.innerHTML = (shownActs.length ? `<div class="pgroup">Actions</div>` : "") +
    shownActs.map((h, i) => row(h, i)).join("") +
    (found.length ? `<div class="pgroup">${terms.length ? "Notes" : "Recent notes"}</div>` : "") +
    found.map((h, i) => row(h, i + shownActs.length)).join("") +
    (hits.length ? "" : `<div class="pr"><span class="ps">Nothing found</span></div>`);
  sel = 0; paint();
}
const row = (h, i) => `<div class="pr" role="option" id="pr${i}" data-i="${i}">${h.html}</div>`;
function paint() {
  pres.querySelectorAll(".pr[data-i]").forEach(el => el.setAttribute("aria-selected", +el.dataset.i === sel));
  pres.querySelector(`[data-i="${sel}"]`)?.scrollIntoView({ block: "nearest" });
}
function go(h) {
  closePalette();
  if (typeof h.go === "function") h.go();
  else location.href = h.go;
}
pin.oninput = () => search();
pin.onkeydown = e => {
  if (e.key === "ArrowDown") { sel = Math.min(sel + 1, hits.length - 1); paint(); e.preventDefault() }
  else if (e.key === "ArrowUp") { sel = Math.max(sel - 1, 0); paint(); e.preventDefault() }
  else if (e.key === "Enter" && hits[sel]) { e.preventDefault(); go(hits[sel]) }
  else if (e.key === "Escape") closePalette();
};
pres.onclick = e => { const el = e.target.closest("[data-i]"); if (el) go(hits[+el.dataset.i]) };
pres.onmousemove = e => { const el = e.target.closest("[data-i]"); if (el && +el.dataset.i !== sel) { sel = +el.dataset.i; paint() } };
pal.onclick = e => { if (e.target === pal) closePalette() };
$("open-search").onclick = openPalette;

// Keys: ⌘K or / to search, N for a new note
addEventListener("keydown", e => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); pal.classList.contains("open") ? closePalette() : openPalette(); return }
  if (e.metaKey || e.ctrlKey || e.altKey || typing() || pal.classList.contains("open")) return;
  if (e.key === "/") { e.preventDefault(); openPalette() }
  else if (e.key === "n") location.href = "/write";
});
