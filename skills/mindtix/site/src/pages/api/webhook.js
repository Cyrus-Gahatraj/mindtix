import { capture } from "../../lib/brain.js";

/**
 * Astro endpoint for Instagram / Meta Graph API Webhook
 * Handles verification (GET) and event reception (POST).
 * Automatically captures incoming Instagram messages into the brain.
 */

export async function GET({ url }) {
  const VERIFY_TOKEN = (process.env.VERIFY_TOKEN || process.env.META_VERIFY_TOKEN || 'cyrus_brain_insta_2026').trim();
  const mode = url.searchParams.get("hub.mode");
  const token = (url.searchParams.get("hub.verify_token") || "").trim();
  const challenge = url.searchParams.get("hub.challenge");

  if (!mode || !token) {
    return Response.json({
      error: "Missing query parameters. Meta sends hub.mode, hub.verify_token, and hub.challenge."
    }, { status: 400 });
  }

  if (mode === "subscribe" && token === VERIFY_TOKEN) {
    return new Response(challenge, {
      status: 200,
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }

  return new Response("Forbidden: Token mismatch", { status: 403 });
}

export async function POST({ request }) {
  const body = await request.json().catch(() => ({}));
  console.log("[Meta Webhook] Event received:", JSON.stringify(body, null, 2));

  try {
    const entries = Array.isArray(body?.entry) ? body.entry : [];
    for (const entry of entries) {
      const messaging = Array.isArray(entry?.messaging) ? entry.messaging : [];
      for (const msg of messaging) {
        const text = msg?.message?.text;
        const sender = msg?.sender?.id;
        if (text) {
          try {
            capture(`Instagram [@${sender || "dm"}]: ${text}`);
          } catch (err) {
            console.warn("[Meta Webhook] Could not capture message:", err.message);
          }
        }
      }
    }
  } catch (err) {
    console.error("[Meta Webhook] Error processing entry:", err);
  }

  return new Response("EVENT_RECEIVED", {
    status: 200,
    headers: { "Content-Type": "text/plain; charset=utf-8" }
  });
}
