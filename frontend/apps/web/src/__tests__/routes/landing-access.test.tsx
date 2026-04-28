import { describe, expect, it } from 'vitest';

import { Route as LandingRoute } from '@/routes/landing';
import { LandingPage } from '@/views/LandingPage';

describe('Landing Route Access', () => {
  it('does not auth-gate /landing (LandingPage is the route component)', () => {
    // Regression test: /landing must remain accessible even when authenticated.
    // Authenticated-only redirect logic should live on "/" or other entry routes, not on "/landing".
    const component = (LandingRoute as unknown as { options?: { component?: unknown } }).options
      ?.component;
    expect(component).toBe(LandingPage);
  });
});
