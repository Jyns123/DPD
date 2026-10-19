import { SqliteRepository } from './sqlite';
import type { AppRepository } from './repository';

const state = globalThis as typeof globalThis & { inmoscoreRepository?: AppRepository };
export function getRepository(): AppRepository {
  if ((process.env.DB_DRIVER || 'sqlite') !== 'sqlite') throw new Error('DB_DRIVER no soportado: registra el adaptador del nuevo motor antes de usarlo.');
  return state.inmoscoreRepository ??= new SqliteRepository();
}
