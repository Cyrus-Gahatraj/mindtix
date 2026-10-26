/**
 * Healthcheck endpoint for Mindtix Instagram Webhook
 */

export default function handler(req, res) {
  if (res.status && res.json) {
    return res.status(200).json({
      status: 'online',
      service: 'Mindtix Instagram Webhook',
      endpoints: {
        webhook: '/api/webhook',
        privacy: '/privacy',
        terms: '/terms',
        data_deletion: '/data-deletion'
      },
      meta_documentation: 'Configure this webhook URL in the Meta Developer Portal'
    });
  }

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify({
    status: 'online',
    service: 'Mindtix Instagram Webhook',
    endpoints: {
      webhook: '/api/webhook',
      privacy: '/privacy',
      terms: '/terms',
      data_deletion: '/data-deletion'
    },
    meta_documentation: 'Configure this webhook URL in the Meta Developer Portal'
  }));
}
