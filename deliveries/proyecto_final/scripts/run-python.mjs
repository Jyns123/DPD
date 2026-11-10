// Usa el entorno del proyecto en Windows, macOS o Linux.
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const [script, ...args] = process.argv.slice(2);
if (!script) throw new Error('Indica el script Python que quieres ejecutar.');
const localPython = resolve(process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const python = process.env.PYTHON_EXECUTABLE || (existsSync(localPython) ? localPython : process.platform === 'win32' ? 'python' : 'python3');
const result = spawnSync(python, [script, ...args], { stdio: 'inherit', shell: false });
if (result.error) {
  console.error('No se pudo iniciar Python. Instala Python 3.12, crea .venv e instala analytics/requirements.txt.');
  process.exitCode = 1;
} else process.exitCode = result.status ?? 1;
