/**
 * Privacy Policy endpoint for Meta Developer Application verification
 */

export default function handler(req, res) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Policy - Mindtix Instagram Webhook</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }
    h1 { color: #111; }
    h2 { margin-top: 24px; color: #333; }
  </style>
</head>
<body>
  <h1>Privacy Policy</h1>
  <p><strong>Effective Date:</strong> October 16, 2026</p>

  <p>This Privacy Policy describes how the Mindtix Instagram Webhook application ("the App") handles information received from the Meta / Instagram platform.</p>

  <h2>1. Information We Receive</h2>
  <p>When you interact with our connected Instagram account (@cyrus.nobody), our application receives webhook event notifications provided by Meta, including:</p>
  <ul>
    <li>Instagram Scoped User ID (an anonymized identifier for the sender)</li>
    <li>Message content (text sent in direct messages)</li>
    <li>Timestamp of the message</li>
  </ul>

  <h2>2. How We Use Information</h2>
  <p>Information received through the webhook is processed exclusively to:</p>
  <ul>
    <li>Provide automated processing and notes synchronization with the Mindtix personal second brain system.</li>
    <li>Troubleshoot application functionality and monitor service health.</li>
  </ul>
  <p>We do not sell, rent, or share user data with third-party advertisers or external data brokers.</p>

  <h2>3. Data Retention and Deletion</h2>
  <p>Data received by the serverless function is processed in real time and is not sold or retained for advertising. If you wish to have your message data deleted from our logs or notes, please see our <a href="/data-deletion">Data Deletion Instructions</a>.</p>

  <h2>4. Contact</h2>
  <p>If you have any questions about this Privacy Policy, you can reach out via GitHub: <a href="https://github.com/Cyrus-Gahatraj/mindtix">github.com/Cyrus-Gahatraj/mindtix</a>.</p>
</body>
</html>`;

  if (res.setHeader && res.status && res.send) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(html);
  }

  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
}
