/**
 * Instagram / Meta Graph API Webhook Endpoint
 * Deployable directly as a Vercel Serverless Function at /api/webhook,
 * or runnable standalone via `node api/webhook.js`
 */

import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** Helper to wrap standard Node HTTP request/response to match Vercel serverless interface */
export function wrapHttp(req, res) {
  if (!req.query && req.url) {
    const parsed = new URL(req.url, "http://localhost");
    req.query = Object.fromEntries(parsed.searchParams);
  }
  if (!res.status) {
    res.status = (code) => {
      res.statusCode = code;
      return res;
    };
  }
  if (!res.send) {
    res.send = (body) => {
      if (typeof body === "string" && !res.getHeader("Content-Type")) {
        res.setHeader("Content-Type", "text/plain; charset=utf-8");
      }
      res.end(body);
      return res;
    };
  }
  if (!res.json) {
    res.json = (body) => {
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      res.end(JSON.stringify(body));
      return res;
    };
  }
}

/**
 * Main Webhook Request Handler (Vercel serverless function & standalone HTTP handler)
 */
export default async function handler(req, res) {
  wrapHttp(req, res);

  // Read verification token from environment variables, or fallback to the token from your dashboard
  const VERIFY_TOKEN = (process.env.VERIFY_TOKEN || process.env.META_VERIFY_TOKEN || 'cyrus_brain_insta_2026').trim();

  // 1. Meta Webhook Verification (GET)
  if (req.method === 'GET') {
    const mode = req.query['hub.mode'];
    const token = (req.query['hub.verify_token'] || '').trim();
    const challenge = req.query['hub.challenge'];

    if (!mode || !token) {
      return res.status(400).json({
        error: 'Missing query parameters. Meta sends hub.mode, hub.verify_token, and hub.challenge.'
      });
    }

    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      console.log('[Meta Webhook] Verification successful!');
      res.setHeader('Content-Type', 'text/plain');
      return res.status(200).send(challenge);
    }

    console.warn(`[Meta Webhook] Token mismatch. Expected: "${VERIFY_TOKEN}", Received: "${token}"`);
    return res.status(403).send('Forbidden: Token mismatch');
  }

  // 2. Incoming Webhook Events (POST)
  if (req.method === 'POST') {
    let body = req.body;
    if (!body && typeof req.on === "function") {
      body = await new Promise((resolve) => {
        let raw = "";
        req.on("data", chunk => raw += chunk);
        req.on("end", () => {
          try { resolve(JSON.parse(raw)); } catch { resolve({}); }
        });
        req.on("error", () => resolve({}));
      });
      req.body = body;
    }

    // Log the event to runtime logs
    console.log('[Meta Webhook] Event received:', JSON.stringify(body, null, 2));

    // Process messages if present
    const entries = Array.isArray(body?.entry) ? body.entry : [];
    for (const entry of entries) {
      const messaging = Array.isArray(entry?.messaging) ? entry.messaging : [];
      for (const msg of messaging) {
        const text = msg?.message?.text;
        const sender = msg?.sender?.id;
        if (text) {
          console.log(`[Meta Webhook] Instagram message from ${sender}: ${text}`);
          const captureUrl = process.env.MINDTIX_CAPTURE_URL;
          if (captureUrl) {
            try {
              fetch(captureUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: `Instagram [@${sender}]: ${text}` })
              }).catch(err => console.warn("[Meta Webhook] Forward to capture failed:", err.message));
            } catch (err) {
              console.warn("[Meta Webhook] Error forwarding to captureUrl:", err.message);
            }
          }
        }
      }
    }

    // Instagram / Meta expects an immediate 200 response
    return res.status(200).send('EVENT_RECEIVED');
  }

  // 3. Method Not Allowed
  res.setHeader('Allow', ['GET', 'POST']);
  return res.status(405).json({ error: `Method ${req.method} not allowed` });
}

// Standalone server when executed directly: `node api/webhook.js`
const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const port = process.env.PORT || 3000;
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);
    if (url.pathname === "/api/webhook") {
      await handler(req, res);
    } else if (url.pathname === "/api" || url.pathname === "/api/") {
      const { default: indexHandler } = await import("./index.js");
      await indexHandler(req, res);
    } else if (url.pathname === "/privacy") {
      const { default: privacyHandler } = await import("./privacy.js");
      await privacyHandler(req, res);
    } else if (url.pathname === "/terms") {
      const { default: termsHandler } = await import("./terms.js");
      await termsHandler(req, res);
    } else if (url.pathname === "/data-deletion") {
      const { default: deletionHandler } = await import("./data-deletion.js");
      await deletionHandler(req, res);
    } else {
      res.statusCode = 404;
      res.setHeader("Content-Type", "text/plain");
      res.end("Not Found");
    }
  });

  server.listen(port, () => {
    console.log(`Mindtix Instagram Webhook server running at http://localhost:${port}`);
    console.log(`Webhook endpoint: http://localhost:${port}/api/webhook`);
  });
}
