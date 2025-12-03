import { createAPIFileRoute, createFileRoute } from '@tanstack/react-router';

/**
 * API Route: POST /api/auth-test
 * Test endpoint for authentication validation
 */
export const Route = createAPIFileRoute('/api/auth-test')({
  POST: async ({ request }) => {
    try {
      // Extract authorization header
      const authHeader = request.headers.get('Authorization');
      const apiKeyHeader = request.headers.get('X-API-Key');

      // Parse request body
      let body: any = {};
      try {
        const contentType = request.headers.get('Content-Type');
        if (contentType?.includes('application/json')) {
          body = await request.json();
        }
      } catch {
        // Body is optional
      }

      // Validate authentication
      const authResults = {
        timestamp: new Date().toISOString(),
        authentication: {
          bearer: {
            present: !!authHeader,
            valid: false,
            token: null as string | null,
            type: null as string | null,
          },
          apiKey: {
            present: !!apiKeyHeader,
            valid: false,
            key: null as string | null,
          },
        },
        request: {
          method: request.method,
          headers: Object.fromEntries(request.headers.entries()),
          body: body,
        },
        message: '',
        authenticated: false,
      };

      // Check Bearer token
      if (authHeader) {
        const [type, token] = authHeader.split(' ');
        authResults.authentication.bearer.type = type;

        if (type === 'Bearer' && token) {
          authResults.authentication.bearer.token = token.substring(0, 10) + '...';

          // Simple validation - in production, validate against your auth service
          if (token.length > 20) {
            authResults.authentication.bearer.valid = true;
            authResults.authenticated = true;
            authResults.message = 'Bearer token authentication successful';
          } else {
            authResults.message = 'Bearer token appears to be invalid';
          }
        } else {
          authResults.message = 'Authorization header format is incorrect';
        }
      }

      // Check API Key
      if (apiKeyHeader) {
        authResults.authentication.apiKey.key = apiKeyHeader.substring(0, 8) + '...';

        // Simple validation - in production, validate against your API key store
        if (apiKeyHeader.length > 16) {
          authResults.authentication.apiKey.valid = true;
          if (!authResults.authenticated) {
            authResults.authenticated = true;
            authResults.message = 'API key authentication successful';
          } else {
            authResults.message += ' (both Bearer and API Key provided)';
          }
        }
      }

      // No authentication provided
      if (!authHeader && !apiKeyHeader) {
        authResults.message = 'No authentication provided. Include either Authorization: Bearer <token> or X-API-Key: <key> header.';

        return new Response(JSON.stringify(authResults), {
          status: 401,
          headers: {
            'Content-Type': 'application/json',
            'WWW-Authenticate': 'Bearer realm="TraceRTM API", charset="UTF-8"',
          },
        });
      }

      // Return results
      const statusCode = authResults.authenticated ? 200 : 401;
      return new Response(JSON.stringify(authResults), {
        status: statusCode,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      console.error('Error in auth test:', error);
      return new Response(
        JSON.stringify({
          error: 'Authentication test failed',
          code: 'AUTH_TEST_ERROR',
          details: error instanceof Error ? error.message : 'Unknown error',
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

  OPTIONS: async () => {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
      },
    });
  },
});
