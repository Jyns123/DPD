import type { DatabaseSync } from 'node:sqlite';
import type { AppRepository, UserRecord } from './repository.ts';
import { openLocalDatabase } from './sqlite-bootstrap.mjs';

function userRow(row: Record<string, unknown> | undefined): UserRecord | null {
  if (!row) return null;
  return { id: String(row.id), email: String(row.email), name: String(row.name),
    passwordHash: String(row.password_hash), profileJson: row.profile_json === null ? null : String(row.profile_json) };
}

export class SqliteRepository implements AppRepository {
  private database: DatabaseSync;
  constructor(filename?: string) { this.database = openLocalDatabase(filename); }
  close() { this.database.close(); }
  async health() { this.database.prepare('SELECT 1').get(); }
  async createUser(user: Omit<UserRecord, 'profileJson'>) {
    const result = this.database.prepare('INSERT INTO users(id,email,name,password_hash) VALUES (?,?,?,?) ON CONFLICT(email) DO NOTHING')
      .run(user.id, user.email, user.name, user.passwordHash);
    return Number(result.changes) ? { ...user, profileJson: null } : null;
  }
  async findUserByEmail(email: string) {
    return userRow(this.database.prepare('SELECT * FROM users WHERE email = ?').get(email));
  }
  async findSessionUser(tokenHash: string, now: number) {
    return userRow(this.database.prepare('SELECT u.* FROM users u JOIN sessions s ON s.user_id = u.id WHERE s.token_hash = ? AND s.expires_at > ?').get(tokenHash, now));
  }
  async createSession(tokenHash: string, userId: string, expiresAt: number) {
    this.database.prepare('DELETE FROM sessions WHERE expires_at <= ?').run(Date.now());
    this.database.prepare('INSERT INTO sessions(token_hash,user_id,expires_at) VALUES (?,?,?)').run(tokenHash, userId, expiresAt);
  }
  async deleteSession(tokenHash: string) { this.database.prepare('DELETE FROM sessions WHERE token_hash = ?').run(tokenHash); }
  async saveProfile(userId: string, name: string, profileJson: string) {
    this.database.prepare('UPDATE users SET name = ?, profile_json = ? WHERE id = ?').run(name, profileJson, userId);
  }
  async listFavorites(userId: string) {
    return this.database.prepare('SELECT listing_id FROM favorites WHERE user_id = ? ORDER BY listing_id').all(userId).map(row => String(row.listing_id));
  }
  async toggleFavorite(userId: string, listingId: string) {
    this.database.exec('BEGIN IMMEDIATE');
    try {
      const existing = this.database.prepare('SELECT 1 FROM favorites WHERE user_id = ? AND listing_id = ?').get(userId, listingId);
      if (existing) this.database.prepare('DELETE FROM favorites WHERE user_id = ? AND listing_id = ?').run(userId, listingId);
      else this.database.prepare('INSERT INTO favorites(user_id,listing_id) VALUES (?,?)').run(userId, listingId);
      this.database.exec('COMMIT');
    } catch (error) { this.database.exec('ROLLBACK'); throw error; }
    return this.listFavorites(userId);
  }
  async deleteAccount(userId: string) {
    // Foreign keys remove all sessions and favorites atomically.
    this.database.prepare('DELETE FROM users WHERE id = ?').run(userId);
  }
  async takeAuthAttempt(key: string, limit: number, windowMs: number) {
    const now = Date.now();
    this.database.prepare('DELETE FROM auth_attempts WHERE reset_at <= ?').run(now);
    this.database.prepare('INSERT INTO auth_attempts(attempt_key,attempts,reset_at) VALUES (?,1,?) ON CONFLICT(attempt_key) DO UPDATE SET attempts = attempts + 1').run(key, now + windowMs);
    const row = this.database.prepare('SELECT attempts FROM auth_attempts WHERE attempt_key = ?').get(key);
    return Number(row?.attempts) <= limit;
  }
  async clearAuthAttempts(key: string) { this.database.prepare('DELETE FROM auth_attempts WHERE attempt_key = ?').run(key); }
}
