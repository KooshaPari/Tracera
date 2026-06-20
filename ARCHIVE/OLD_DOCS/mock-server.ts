// Mock server for E2E tests
import { serve } from "bun";

const server = serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url);
    const path = url.pathname;

    // Mock responses for all routes
    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Mock App</title>
        </head>
        <body>
          <div data-testid="content">
            <h1>Mock Application</h1>
            <p>Path: ${path}</p>
          </div>
        </body>
      </html>
    `;

    return new Response(html, {
      headers: { "Content-Type": "text/html" },
    });
  },
});

console.log(`✅ Mock server running on http://localhost:${server.port}`);

