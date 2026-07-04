import '@testing-library/user-event';

declare global {
  var user: ReturnType<typeof import('@testing-library/user-event').default.setup>;
}
