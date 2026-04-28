// @ts-expect-error - pg types not always available
import { Client } from 'pg';
import { createHash } from 'crypto';

interface QueryResult {
  rows: Array<{ id: string; email: string }>;
}

async function seedTestUser(): Promise<void> {
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    console.warn('⚠️ DATABASE_URL not set - skipping database seeding');
    return;
  }

  const client = new Client({
    connectionString: databaseUrl,
  });

  try {
    await client.connect();
    console.log('📦 Seeding test user to database...');

    const testEmail = 'kooshapari@kooshapari.com';
    const testPassword = 'testAdmin123';

    const hashedPassword = createHash('sha256').update(testPassword).digest('hex');

    const result = (await client.query(
      `INSERT INTO users (id, email, name, password_hash, role, created_at)
       VALUES ($1, $2, $3, $4, $5, NOW())
       ON CONFLICT (email) DO UPDATE SET password_hash = $4
       RETURNING id, email`,
      [
        `test-admin-${Date.now()}`,
        testEmail,
        'Test Admin',
        hashedPassword,
        'admin',
      ],
    )) as QueryResult;

    console.log(`✅ Database test user created/updated:`, result.rows[0]);
  } catch (error) {
    console.error('❌ Database seeding failed:', error);
    throw error;
  } finally {
    await client.end();
  }
}

seedTestUser().catch((error) => {
  console.error('Fatal error:', error);
  // eslint-disable-next-line no-process-exit
  process.exit(1);
});
