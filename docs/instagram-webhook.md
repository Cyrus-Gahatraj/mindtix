# Instagram Webhook for Mindtix

Mindtix includes a built-in webhook receiver for the Meta / Instagram Graph API, allowing real-time message events from Instagram to sync directly into your Mindtix brain.

## Endpoints

| Endpoint | Path | Description |
|---|---|---|
| **Webhook Callback** | `GET /api/webhook` | Meta verification handshake (`hub.challenge`) |
| **Webhook Receiver** | `POST /api/webhook` | Receives incoming messages and event payloads |
| **Healthcheck** | `GET /api` | Service status and endpoint metadata |
| **Privacy Policy** | `GET /privacy` | Meta compliance Privacy Policy |
| **Terms of Service** | `GET /terms` | Meta compliance Terms of Service |
| **Data Deletion** | `GET /data-deletion` | Meta compliance User Data Deletion Instructions |

---

## Deployment & Setup

### Option A: Deploy to Vercel (Cloud Serverless)

1. **Deploy repository**:
   - Go to [vercel.com/new](https://vercel.com/new).
   - Import your Mindtix repository (`Cyrus-Gahatraj/mindtix`).
   - In **Environment Variables**, add:
     - `VERIFY_TOKEN`: your secret verification token (e.g. `cyrus_brain_insta_2026`).
     - *(Optional)* `MINDTIX_CAPTURE_URL`: public URL of your Mindtix site capture endpoint (e.g. `https://<your-site>/api/capture`) to automatically capture DMs into your notes.
   - Click **Deploy**.

2. **Configure in Meta App Dashboard**:
   - Open [developers.facebook.com](https://developers.facebook.com/) -> Your App -> **Webhooks** -> **Instagram**.
   - **Callback URL**: `https://<your-project>.vercel.app/api/webhook`
   - **Verify Token**: the exact same string configured in `VERIFY_TOKEN`.
   - Click **Verify and Save**.
   - Subscribe to the `messages` field.

3. **App Review & Compliance URLs**:
   In **App Settings > Basic**, set:
   - **Privacy Policy URL**: `https://<your-project>.vercel.app/privacy`
   - **Terms of Service URL**: `https://<your-project>.vercel.app/terms`
   - **User Data Deletion Callback / URL**: `https://<your-project>.vercel.app/data-deletion`

---

### Option B: Local Standalone Server

You can run the webhook server locally using standard Node.js:

```sh
npm start
# or: VERIFY_TOKEN=your_token node api/webhook.js
```

The server listens on `http://localhost:3000` (or `PORT`). Expose it to Meta using a tunnel:

```sh
cloudflared tunnel --url http://localhost:3000
# or: ngrok http 3000
```

---

### Option C: In the Mindtix Web App (`skills/mindtix/site`)

The Mindtix web app has the Instagram webhook endpoint built right into its Astro server (`/api/webhook`):

1. Start your Mindtix site (`npm run dev` inside `<brain>/exports/site` or `skills/mindtix/site`).
2. Tunnel port 4321 to a public HTTPS URL (e.g., with cloudflared or ngrok).
3. Any incoming Instagram Direct Messages sent to your connected account are automatically captured into today's note (`notes/YYYY-MM-DD.md`) with timestamps and sender IDs!
