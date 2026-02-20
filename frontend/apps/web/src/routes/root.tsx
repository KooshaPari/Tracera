import { createFileRoute, Navigate } from '@tanstack/react-router';

const IndexRoute = () => <Navigate to='/landing' />;

export const Route = createFileRoute('/')({
  component: IndexRoute,
});
