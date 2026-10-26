import assert from "node:assert/strict";
import http from "node:http";
import { test } from "node:test";
import webhookHandler from "../api/webhook.js";
import indexHandler from "../api/index.js";
import privacyHandler from "../api/privacy.js";
import termsHandler from "../api/terms.js";
import deletionHandler from "../api/data-deletion.js";
import * as siteWebhook from "../skills/mindtix/site/src/pages/api/webhook.js";

// Helper to make mock request/response objects
function mockReqRes({ method = "GET", url = "/", body = null, query = {} } = {}) {
  const req = {
    method,
    url,
    query,
    body
  };
  let statusCode = 200;
  let headers = {};
  let sentData = null;

  const res = {
    statusCode,
    status(code) {
      this.statusCode = code;
      statusCode = code;
      return this;
    },
    setHeader(key, val) {
      headers[key.toLowerCase()] = val;
      return this;
    },
    getHeader(key) {
      return headers[key.toLowerCase()];
    },
    send(data) {
      sentData = data;
      return this;
    },
    json(data) {
      this.setHeader("Content-Type", "application/json");
      sentData = JSON.stringify(data);
      return this;
    },
    end(data) {
      if (data !== undefined) sentData = data;
      return this;
    },
    get _body() {
      return sentData;
    },
    get _status() {
      return this.statusCode;
    }
  };

  return { req, res };
}

test("webhook GET verification succeeds with correct token", async () => {
  const token = process.env.VERIFY_TOKEN || "cyrus_brain_insta_2026";
  const { req, res } = mockReqRes({
    method: "GET",
    url: `/api/webhook?hub.mode=subscribe&hub.verify_token=${token}&hub.challenge=test_challenge_123`,
    query: {
      "hub.mode": "subscribe",
      "hub.verify_token": token,
      "hub.challenge": "test_challenge_123"
    }
  });

  await webhookHandler(req, res);
  assert.equal(res._status, 200);
  assert.equal(res._body, "test_challenge_123");
});

test("webhook GET verification fails with token mismatch", async () => {
  const { req, res } = mockReqRes({
    method: "GET",
    url: "/api/webhook?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=test_challenge_123",
    query: {
      "hub.mode": "subscribe",
      "hub.verify_token": "wrong_token",
      "hub.challenge": "test_challenge_123"
    }
  });

  await webhookHandler(req, res);
  assert.equal(res._status, 403);
  assert.match(res._body, /Forbidden/);
});

test("webhook GET verification fails when parameters are missing", async () => {
  const { req, res } = mockReqRes({
    method: "GET",
    url: "/api/webhook",
    query: {}
  });

  await webhookHandler(req, res);
  assert.equal(res._status, 400);
  assert.match(res._body, /Missing query parameters/);
});

test("webhook POST handles incoming event and returns EVENT_RECEIVED", async () => {
  const samplePayload = {
    object: "instagram",
    entry: [
      {
        id: "17841400000000000",
        time: 1700000000,
        messaging: [
          {
            sender: { id: "123456789" },
            recipient: { id: "987654321" },
            timestamp: 1700000000000,
            message: {
              mid: "m_mid123",
              text: "Review graphs chapter tomorrow"
            }
          }
        ]
      }
    ]
  };

  const { req, res } = mockReqRes({
    method: "POST",
    url: "/api/webhook",
    body: samplePayload
  });

  await webhookHandler(req, res);
  assert.equal(res._status, 200);
  assert.equal(res._body, "EVENT_RECEIVED");
});

test("healthcheck GET /api returns online status", () => {
  const { req, res } = mockReqRes({ method: "GET", url: "/api" });
  indexHandler(req, res);
  assert.equal(res._status, 200);
  const data = JSON.parse(res._body);
  assert.equal(data.status, "online");
  assert.equal(data.service, "Mindtix Instagram Webhook");
  assert.equal(data.endpoints.webhook, "/api/webhook");
});

test("policy endpoints serve HTML documents", () => {
  for (const [handler, titleMatch] of [
    [privacyHandler, /Privacy Policy/],
    [termsHandler, /Terms of Service/],
    [deletionHandler, /User Data Deletion/]
  ]) {
    const { req, res } = mockReqRes({ method: "GET" });
    handler(req, res);
    assert.equal(res._status, 200);
    assert.match(res._body, titleMatch);
    assert.match(res._body, /github\.com\/Cyrus-Gahatraj\/mindtix/);
  }
});

test("Astro site webhook endpoint handles GET verification and POST events", async () => {
  const token = process.env.VERIFY_TOKEN || "cyrus_brain_insta_2026";
  const getUrl = new URL(`http://localhost/api/webhook?hub.mode=subscribe&hub.verify_token=${token}&hub.challenge=astro_challenge`);
  const getRes = await siteWebhook.GET({ url: getUrl });
  assert.equal(getRes.status, 200);
  assert.equal(await getRes.text(), "astro_challenge");

  const postReq = new Request("http://localhost/api/webhook", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      object: "instagram",
      entry: []
    })
  });
  const postRes = await siteWebhook.POST({ request: postReq });
  assert.equal(postRes.status, 200);
  assert.equal(await postRes.text(), "EVENT_RECEIVED");
});
