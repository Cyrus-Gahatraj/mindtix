// A stand-in for the `claude` CLI in tests: records how it was called, then streams like `claude -p --output-format stream-json`.
import fs from "node:fs";
const args = process.argv.slice(2);
if (args.includes("--version")) { console.log("9.9.9 (fake)"); process.exit(0) }
let input = "";
process.stdin.on("data", d => { input += d }).on("end", () => {
  fs.appendFileSync(process.env.FAKE_CLAUDE_LOG, JSON.stringify({ args, input, claudecode: process.env.CLAUDECODE ?? null, cwd: process.cwd() }) + "\n");
  const out = o => process.stdout.write(JSON.stringify(o) + "\n");
  const sid = args[args.indexOf(args.includes("--resume") ? "--resume" : "--session-id") + 1];
  out({ type: "system", subtype: "init", session_id: sid });
  if (input.includes("fail")) { out({ type: "result", subtype: "error_during_execution", is_error: true, result: "Something broke" }); process.exit(1) }
  const say = text => out({ type: "stream_event", event: { type: "content_block_delta", index: 0, delta: { type: "text_delta", text } } });
  say("Let me look.");
  out({ type: "assistant", message: { content: [{ type: "tool_use", name: "Read", input: { file_path: process.cwd() + "/knowledge/sql-joins.md" } }] } });
  out({ type: "assistant", message: { content: [{ type: "tool_use", name: "TodoWrite", input: {} }] } });
  say("A left join keeps ");
  say("every row. [[sql-joins]]");
  out({ type: "result", subtype: "success", is_error: false, result: "A left join keeps every row. [[sql-joins]]", session_id: sid });
});
