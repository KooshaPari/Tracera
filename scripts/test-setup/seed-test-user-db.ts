import { Client } from 'pg';
import * as crypto from 'crypto';

async function seedTestUser() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
  });

  try {
    await client.connect();
    console.log('📦 Seeding test user to database...');

    const testEmail = 'kooshapari@kooshapari.com';
    const testPassword = 'testAdmin123';

    const hashedPassword = crypto.createHash('sha256').update(testPassword).digest('hex');

    const result = await client.query(
      `INSERT INTO users (id, email, name, password_hash, role, created_at)
       VALUES ($1, $2, $3, $4, $5, NOW())
       ON CONFLICT (email) DO UPDATE SET password_hash = $4
       RETURNING id, email`,
      [
        'test-admin-' + Date.now(),
        testEmail,
        'Test Admin',
        hashedPassword,
        'admin',
      ],
    );

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
  process.exit(1);
});
