interface UserMetadata extends Record<
  string,
  string | number | boolean | object | null | undefined
> {}

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
  role?: string;
  metadata?: UserMetadata;
}
