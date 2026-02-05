import { Client } from '@workos-inc/node';

const client = new Client({
  apiKey: process.env.WORKOS_API_KEY,
});

interface TestUserOptions {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  organizationId: string;
}

async function createTestUser(opts: TestUserOptions) {
  try {
    console.log(`Creating test user: ${opts.email}`);

    let workosUser;
    try {
      workosUser = await client.userManagement.createUser({
        email: opts.email,
        firstName: opts.firstName,
        lastName: opts.lastName,
        organizationId: opts.organizationId,
        password: opts.password,
      });
      console.log(`✅ WorkOS user created: ${workosUser.id}`);
    } catch (error: any) {
      if (error.message?.includes('already exists')) {
        console.log(`⚠️ WorkOS user already exists: ${opts.email}`);
        workosUser = null;
      } else {
        throw error;
      }
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
