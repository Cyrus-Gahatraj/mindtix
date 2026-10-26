/**
 * Terms of Service endpoint for Meta Developer Application verification
 */

export default function handler(req, res) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Terms of Service - Mindtix Instagram Webhook</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }
    h1 { color: #111; }
    h2 { margin-top: 24px; color: #333; }
  </style>
</head>
<body>
  <h1>Terms of Service</h1>
  <p><strong>Effective Date:</strong> October 16, 2026</p>

  <h2>1. Acceptance of Terms</h2>
  <p>By interacting with the Mindtix Instagram integration or sending messages to our connected account, you acknowledge and agree to these Terms of Service.</p>

  <h2>2. Use of Service</h2>
  <p>This service operates as a webhook listener for personal automation, note taking, and productivity integration using the Meta Graph API. The service is provided "as is" without warranty of any kind.</p>

  <h2>3. Compliance with Platform Policies</h2>
  <p>This application complies with Meta Platform Terms and Developer Policies. Users must not use this integration to transmit illegal, harassing, or abusive content.</p>

  <h2>4. Contact</h2>
  <p>For questions regarding these Terms, contact us via GitHub at <a href="https://github.com/Cyrus-Gahatraj/mindtix">github.com/Cyrus-Gahatraj/mindtix</a>.</p>
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
