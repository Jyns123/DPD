import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { openLocalDatabase } from '../db/sqlite-bootstrap.mjs';
import { bindOptions } from './bind-options.mjs';

const [mode = 'dev', ...args] = process.argv.slice(2);
if (!['dev', 'start', 'build'].includes(mode)) throw new Error('Modo de arranque inválido.');
const require = createRequire(import.meta.url);
require('@next/env').loadEnvConfig(process.cwd(), mode === 'dev');
let localOnly = false;
if (mode !== 'build') {
const binding = bindOptions(args);
args.splice(0, args.length, ...binding.args);
localOnly = binding.localOnly;
const database = openLocalDatabase();
database.close();
console.log('SQLite local lista; esquema verificado.');
if (!args.some(arg => arg === '--port' || arg === '-p' || arg.startsWith('--port='))) args.push('--port', '5173');
}
const next = require.resolve('next/dist/bin/next');
// El acceso sin clave solo existe cuando este proceso escucha en loopback.
// Un encabezado Host manipulado no debe habilitar un tablero público.
const child = spawn(process.execPath, [next, mode, ...args], { stdio: 'inherit', env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1', ANALYTICS_LOCAL_ONLY: localOnly ? '1' : '0' } });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
child.on('exit', (code, signal) => { process.exitCode = code ?? (signal === 'SIGINT' ? 0 : 1); });
