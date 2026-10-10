import { load } from "../lib/brain.js";
import { fcIndex } from "../lib/ui.js";
export const GET = () => Response.json(load().notes.map(({ id, folder, title, text, mod }) => ({ id, folder, title, text, mod, c: fcIndex(folder) })));
