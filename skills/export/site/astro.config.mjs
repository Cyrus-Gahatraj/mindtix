import { defineConfig } from "astro/config";
import node from "@astrojs/node";

// Every page is rendered on request, straight from the notes, so edits show on refresh
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { host: "127.0.0.1", port: 4321 },
  devToolbar: { enabled: false },
});
