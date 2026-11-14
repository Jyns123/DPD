import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import type { EventInput } from '../lib/analytics-validation.ts';

export const MAX_EVENTS = 20000;
export class AnalyticsStore {
  private database: DatabaseSync;
  constructor(filename = process.env.ANALYTICS_PATH || 'storage/analytics.sqlite') {
    const path = resolve(filename);
    mkdirSync(dirname(path), {recursive: true});
    this.database = new DatabaseSync(path);
    this.database.exec(`PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, visitor_id TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL);
      CREATE INDEX IF NOT EXISTS events_date ON events(timestamp);
      CREATE INDEX IF NOT EXISTS events_visitor ON events(visitor_id, timestamp);`);
  }
  close() { this.database.close(); }
  record(input: EventInput, now = new Date()) {
    const timestamp = now.toISOString();
    this.database.exec('BEGIN IMMEDIATE');
    try {
      if (this.database.prepare('SELECT 1 FROM events WHERE id=?').get(input.id)) {
        this.database.exec('COMMIT'); return 'duplicate' as const;
      }
      const recent = this.database.prepare('SELECT COUNT(*) AS n FROM events WHERE visitor_id=? AND timestamp>=?')
        .get(input.visitorId, new Date(now.getTime()-60000).toISOString());
      if (Number(recent?.n) >= 100) { this.database.exec('COMMIT'); return 'limited' as const; }
      // No deducimos un canal de marketing sin una fuente de atribución.
      const event = {...input, timestamp};
      this.database.prepare('INSERT INTO events(id,visitor_id,timestamp,payload) VALUES (?,?,?,?)')
        .run(input.id,input.visitorId,timestamp,JSON.stringify(event));
      this.database.prepare('DELETE FROM events WHERE timestamp<?').run(new Date(now.getTime()-90*86400000).toISOString());
      this.database.prepare('DELETE FROM events WHERE id IN (SELECT id FROM events ORDER BY timestamp DESC, rowid DESC LIMIT -1 OFFSET ?)').run(MAX_EVENTS);
      this.database.exec('COMMIT');
      return 'saved' as const;
    } catch (error) { this.database.exec('ROLLBACK'); throw error; }
  }
  list() {
    const cutoff = new Date(Date.now()-90*86400000).toISOString();
    // La conservación se aplica también al consultar, aunque no haya visitas nuevas.
    this.database.prepare('DELETE FROM events WHERE timestamp<?').run(cutoff);
    return this.database.prepare('SELECT payload FROM events WHERE timestamp>=? ORDER BY timestamp, rowid').all(cutoff)
      .map(row => JSON.parse(String(row.payload)));
  }
  revision() {
    const cutoff = new Date(Date.now()-90*86400000).toISOString();
    this.database.prepare('DELETE FROM events WHERE timestamp<?').run(cutoff);
    const count = this.database.prepare('SELECT COUNT(*) AS n FROM events').get();
    const latest = this.database.prepare('SELECT id FROM events ORDER BY rowid DESC LIMIT 1').get();
    // El contenido es inmutable: cambian el último ID o el total al insertar o limpiar.
    return `${Number(count?.n || 0)}:${String(latest?.id || 'empty')}`;
  }
}
