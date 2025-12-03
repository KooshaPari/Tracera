import { createFileRoute } from '@tanstack/react-router';
import { SwaggerUIWrapper } from '@/components/api-docs/swagger-ui-wrapper';

export const Route = createFileRoute('/api-docs/swagger')({
  component: SwaggerPage,
  head: () => ({
    meta: [
      {
        title: 'API Documentation - Swagger UI | TraceRTM',
      },
      {
        name: 'description',
        content:
          'Interactive API documentation for TraceRTM using Swagger UI. Test API endpoints, view request/response schemas, and try out API calls.',
      },
    ],
  }),
});

function SwaggerPage() {
  return (
    <div className="swagger-page">
      <SwaggerUIWrapper
        specUrl="/specs/openapi.json"
        tryItOutEnabled={true}
        persistAuthorization={true}
        displayRequestDuration={true}
        filter={true}
        deepLinking={true}
      />
    </div>
  );
}
