import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, readFileSync, chmodSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

// Shared by the startup script and the SQLite adapter. No database is shipped.
export function openLocalDatabase(filename = process.env.SQLITE_PATH || 'storage/inmoscore.sqlite') {
  if ((process.env.DB_DRIVER || 'sqlite') !== 'sqlite') {
    throw new Error('DB_DRIVER no soportado. Implementa y registra otro adaptador antes de cambiar el motor.');
  }
  const path = resolve(process.cwd(), filename);
  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  const database = new DatabaseSync(path);
  chmodSync(path, 0o600);
  database.exec('PRAGMA busy_timeout = 5000; PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;');
  try {
    database.exec('BEGIN IMMEDIATE');
    const version = Number(database.prepare('PRAGMA user_version').get()?.user_version || 0);
    if (version > 1) throw new Error('La base usa una versión de esquema más reciente que esta aplicación.');
    if (version < 1) database.exec(readFileSync(new URL('./migrations/sqlite/001-initial.sql', import.meta.url), 'utf8'));
    database.exec('COMMIT');
    return database;
  } catch (error) {
    database.exec('ROLLBACK');
    database.close();
    throw error;
  }
}
