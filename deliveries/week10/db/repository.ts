export type UserRecord = {
  id: string;
  email: string;
  name: string;
  passwordHash: string;
  profileJson: string | null;
};

// Routes depend on this async contract, not on SQL dialects. A future RDS
// PostgreSQL/MySQL adapter can implement it with its own pool and migrations.
export interface AppRepository {
  health(): Promise<void>;
  createUser(user: Omit<UserRecord, 'profileJson'>): Promise<UserRecord | null>;
  findUserByEmail(email: string): Promise<UserRecord | null>;
  findSessionUser(tokenHash: string, now: number): Promise<UserRecord | null>;
  createSession(tokenHash: string, userId: string, expiresAt: number): Promise<void>;
  deleteSession(tokenHash: string): Promise<void>;
  saveProfile(userId: string, name: string, profileJson: string): Promise<void>;
  listFavorites(userId: string): Promise<string[]>;
  toggleFavorite(userId: string, listingId: string): Promise<string[]>;
  deleteAccount(userId: string): Promise<void>;
  takeAuthAttempt(key: string, limit: number, windowMs: number): Promise<boolean>;
  clearAuthAttempts(key: string): Promise<void>;
}
