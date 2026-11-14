import type { DatabaseSync, StatementSync } from 'node:sqlite';
import type { AppRepository, UserRecord } from './repository.ts';
import { openLocalDatabase } from './sqlite-bootstrap.mjs';

function userRow(row: Record<string, unknown> | undefined): UserRecord | null {
  if (!row) return null;
  return { id: String(row.id), email: String(row.email), name: String(row.name),
    passwordHash: String(row.password_hash), profileJson: row.profile_json === null ? null : String(row.profile_json) };
}

export class SqliteRepository implements AppRepository {
  private database: DatabaseSync;
  private statements = new Map<string, StatementSync>();
  private lastCleanup = 0;
  constructor(filename?: string) { this.database = openLocalDatabase(filename); }
  private statement(sql: string) {
    let statement = this.statements.get(sql);
    if (!statement) { statement = this.database.prepare(sql); this.statements.set(sql, statement); }
    return statement;
  }
  private cleanupExpired(now: number) {
    if (now - this.lastCleanup < 60000) return;
    this.statement('DELETE FROM sessions WHERE expires_at <= ?').run(now);
    this.statement('DELETE FROM auth_attempts WHERE reset_at <= ?').run(now);
    this.lastCleanup = now;
  }
  close() { this.statements.clear(); this.database.close(); }
  async health() { this.statement('SELECT 1').get(); }
  async createUser(user: Omit<UserRecord, 'profileJson'>) {
    const result = this.statement('INSERT INTO users(id,email,name,password_hash) VALUES (?,?,?,?) ON CONFLICT(email) DO NOTHING')
      .run(user.id, user.email, user.name, user.passwordHash);
    return Number(result.changes) ? { ...user, profileJson: null } : null;
  }
  async findUserByEmail(email: string) {
    return userRow(this.statement('SELECT * FROM users WHERE email = ?').get(email));
  }
  async findSessionUser(tokenHash: string, now: number) {
    return userRow(this.statement('SELECT u.* FROM users u JOIN sessions s ON s.user_id = u.id WHERE s.token_hash = ? AND s.expires_at > ?').get(tokenHash, now));
  }
  async createSession(tokenHash: string, userId: string, expiresAt: number) {
    this.cleanupExpired(Date.now());
    this.statement('INSERT INTO sessions(token_hash,user_id,expires_at) VALUES (?,?,?)').run(tokenHash, userId, expiresAt);
  }
  async deleteSession(tokenHash: string) { this.statement('DELETE FROM sessions WHERE token_hash = ?').run(tokenHash); }
  async saveProfile(userId: string, name: string, profileJson: string) {
    this.statement('UPDATE users SET name = ?, profile_json = ? WHERE id = ?').run(name, profileJson, userId);
  }
  async listFavorites(userId: string) {
    return this.statement('SELECT listing_id FROM favorites WHERE user_id = ? ORDER BY listing_id').all(userId).map(row => String(row.listing_id));
  }
  async toggleFavorite(userId: string, listingId: string) {
    this.database.exec('BEGIN IMMEDIATE');
    try {
      const existing = this.statement('SELECT 1 FROM favorites WHERE user_id = ? AND listing_id = ?').get(userId, listingId);
      if (existing) this.statement('DELETE FROM favorites WHERE user_id = ? AND listing_id = ?').run(userId, listingId);
      else this.statement('INSERT INTO favorites(user_id,listing_id) VALUES (?,?)').run(userId, listingId);
      this.database.exec('COMMIT');
    } catch (error) { this.database.exec('ROLLBACK'); throw error; }
    return this.listFavorites(userId);
  }
  async deleteAccount(userId: string) {
    // Foreign keys remove all sessions and favorites atomically.
    this.statement('DELETE FROM users WHERE id = ?').run(userId);
  }
  async takeAuthAttempt(key: string, limit: number, windowMs: number) {
    const now = Date.now();
    this.cleanupExpired(now);
    // Actualización y lectura atómicas, incluso con dos procesos sobre el mismo archivo.
    const row = this.statement(`INSERT INTO auth_attempts(attempt_key,attempts,reset_at) VALUES (?,1,?)
      ON CONFLICT(attempt_key) DO UPDATE SET
      attempts=CASE WHEN reset_at<=? THEN 1 ELSE MIN(attempts+1,?) END,
      reset_at=CASE WHEN reset_at<=? THEN excluded.reset_at ELSE reset_at END
      RETURNING attempts`).get(key, now + windowMs, now, limit + 1, now);
    return Number(row?.attempts) <= limit;
  }
  async clearAuthAttempts(key: string) { this.statement('DELETE FROM auth_attempts WHERE attempt_key = ?').run(key); }
}
