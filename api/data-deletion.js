/**
 * Data Deletion instructions endpoint for Meta Developer Application verification
 */

export default function handler(req, res) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>User Data Deletion Instructions - Mindtix Instagram Webhook</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }
    h1 { color: #111; }
    h2 { margin-top: 24px; color: #333; }
    ol { padding-left: 20px; }
    li { margin-bottom: 8px; }
  </style>
</head>
<body>
  <h1>User Data Deletion Instructions</h1>
  <p>In accordance with Meta Platform policies, users have the right to request the deletion of any data associated with their Instagram interactions with this application.</p>

  <h2>How to Request Data Deletion</h2>
  <p>If you have sent messages or interacted with our application and wish to delete your data from our temporary logs or records:</p>
  <ol>
    <li>Send an Instagram Direct Message with the exact phrase <strong>"DELETE MY DATA"</strong> to <code>@cyrus.nobody</code>, OR</li>
    <li>Open an issue or submit a deletion request via our repository: <a href="https://github.com/Cyrus-Gahatraj/mindtix/issues">github.com/Cyrus-Gahatraj/mindtix/issues</a> including your Instagram Scoped User ID.</li>
  </ol>
  <p>Upon receipt, any associated event logs will be permanently deleted within 48 hours.</p>
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
