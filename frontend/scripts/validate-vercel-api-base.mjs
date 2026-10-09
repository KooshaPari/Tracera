#!/usr/bin/env node

// Vercel deploys route /api/* through the same-origin catch-all Function.
// This applies only to the Vercel workflow; local gateway and desktop builds
// may still use an explicit loopback API base.
if (process.env.VITE_API_URL !== '/api') {
  console.error('Vercel builds require VITE_API_URL=/api (same-origin gateway)');
  process.exit(1);
}

console.log('PASS Vercel API base (/api, same-origin gateway)');
