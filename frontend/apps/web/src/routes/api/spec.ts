import { createAPIFileRoute, createFileRoute } from '@tanstack/react-router';
import fs from 'node:fs';
import path from 'node:path';

/**
 * API Route: GET /api/spec
 * Returns the OpenAPI specification
 */
export const Route = createAPIFileRoute('/api/spec')({
  GET: async ({ request }) => {
    try {
      // Read the OpenAPI spec from public directory
      const specPath = path.join(
        process.cwd(),
        'public',
        'specs',
        'openapi.json'
      );

      // Check if file exists
      if (!fs.existsSync(specPath)) {
        return new Response(
          JSON.stringify({
            error: 'OpenAPI specification not found',
            code: 'SPEC_NOT_FOUND',
          }),
          {
            status: 404,
            headers: {
              'Content-Type': 'application/json',
              'Cache-Control': 'no-cache',
            },
          }
        );
      }

      // Read and parse the spec
      const specContent = fs.readFileSync(specPath, 'utf-8');
      const spec = JSON.parse(specContent);

      // Return the spec with proper headers
      return new Response(JSON.stringify(spec), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=3600', // Cache for 1 hour
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    } catch (error) {
      console.error('Error serving OpenAPI spec:', error);
      return new Response(
        JSON.stringify({
          error: 'Failed to load OpenAPI specification',
          code: 'INTERNAL_ERROR',
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
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  },
});
