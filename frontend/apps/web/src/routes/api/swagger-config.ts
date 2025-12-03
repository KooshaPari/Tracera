import { createAPIFileRoute, createFileRoute } from '@tanstack/react-router';

/**
 * API Route: GET /api/swagger-config
 * Returns Swagger UI configuration
 */
export const Route = createAPIFileRoute('/api/swagger-config')({
  GET: async ({ request }) => {
    try {
      const config = {
        apiUrl: process.env.API_URL || 'http://localhost:8000',
        authType: 'bearer',
        persistAuth: true,
        tryItOut: true,
        displayRequestDuration: true,
        filter: true,
        deepLinking: true,
        docExpansion: 'list',
        defaultModelsExpandDepth: 1,
        supportedSubmitMethods: [
          'get',
          'put',
          'post',
          'delete',
          'options',
          'head',
          'patch',
        ],
        oauth2RedirectUrl: `${process.env.PUBLIC_URL || 'http://localhost:3000'}/api-docs/swagger/oauth2-redirect.html`,
        requestInterceptor: {
          enabled: true,
          addAuthHeader: true,
          addCorsHeaders: true,
        },
        responseInterceptor: {
          enabled: true,
          logResponses: true,
        },
      };

      return new Response(JSON.stringify(config), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=300', // Cache for 5 minutes
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      console.error('Error serving Swagger config:', error);
      return new Response(
        JSON.stringify({
          error: 'Failed to load Swagger configuration',
          code: 'CONFIG_ERROR',
        }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }
  },
});
