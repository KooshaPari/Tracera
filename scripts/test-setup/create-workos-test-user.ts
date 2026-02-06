import type { Client as WorkOSClient } from '@workos-inc/node';

// Import with dynamic require to handle optional dependency
let client: WorkOSClient | null = null;

try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { Client } = require('@workos-inc/node');
  if (process.env.WORKOS_API_KEY) {
    client = new Client({
      apiKey: process.env.WORKOS_API_KEY,
    });
  }
} catch {
  // WorkOS SDK not available - will skip WorkOS user creation
}

interface TestUserOptions {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  organizationId: string;
}

interface WorkOSUser {
  id: string;
}

async function createTestUser(opts: TestUserOptions): Promise<{
  email: string;
  password: string;
  workosId: string | undefined;
  status: string;
}> {
  try {
    console.log(`Creating test user: ${opts.email}`);

    let workosUser: WorkOSUser | null = null;
    if (client) {
      try {
        workosUser = await client.userManagement.createUser({
          email: opts.email,
          firstName: opts.firstName,
          lastName: opts.lastName,
          organizationId: opts.organizationId,
          password: opts.password,
        });
        console.log(`✅ WorkOS user created: ${workosUser.id}`);
      } catch (error: unknown) {
        const err = error as Error;
        if (err.message?.includes('already exists')) {
          console.log(`⚠️ WorkOS user already exists: ${opts.email}`);
          workosUser = null;
        } else {
          throw error;
        }
      }
    } else {
      console.log(`⚠️ WorkOS SDK not available - skipping WorkOS user creation`);
    }

    return {
      email: opts.email,
      password: opts.password,
      workosId: workosUser?.id,
      status: 'created',
    };
  } catch (error) {
    console.error(`❌ Failed to create WorkOS test user:`, error);
    throw error;
  }
}

async function main() {
  const testUsers = [
    {
      email: 'kooshapari@kooshapari.com',
      password: 'testAdmin123',
      firstName: 'Test',
      lastName: 'Admin',
      organizationId: process.env.WORKOS_ORG_ID || 'test-org',
    },
  ];

  for (const user of testUsers) {
    await createTestUser(user);
  }

  console.log('✅ Test user setup complete');
}

main().catch((error) => {
  console.error('Setup failed:', error);
  process.exit(1);
});
