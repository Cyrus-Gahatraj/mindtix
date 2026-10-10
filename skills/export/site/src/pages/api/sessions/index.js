import { sessions } from "../../../lib/ask.js";
export const GET = () => Response.json(sessions());
