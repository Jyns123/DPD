import { isIP } from 'node:net';

/** Entrega un único hostname al CLI; el guard usa exactamente ese mismo valor. */
export function bindOptions(args) {
  const forwarded = [];
  let hostname;
  for (let index = 0; index < args.length; index++) {
    const arg = args[index];
    if (arg === '--') throw new Error('No repitas el separador -- dentro de los argumentos del servidor.');
    if (arg.startsWith('-H') && arg !== '-H') throw new Error('Usa -H seguido de un espacio y el hostname; no uses la forma adjunta.');
    const separate = arg === '--hostname' || arg === '-H';
    const assigned = arg.startsWith('--hostname=');
    if (!separate && !assigned) {
      if (arg.startsWith('--hostname')) throw new Error('La opción de escucha es --hostname o -H.');
      forwarded.push(arg); continue;
    }
    if (hostname !== undefined) throw new Error('Indica el hostname una sola vez para evitar una configuración ambigua.');
    const value = separate ? args[++index] : arg.slice('--hostname='.length);
    const validName = typeof value === 'string' && value.length <= 253 &&
      /^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.?$/.test(value);
    if (typeof value !== 'string' || !value || (!isIP(value) && !validName)) {
      throw new Error('Indica un hostname o una IP válidos, sin protocolo ni puerto. Para IPv6 usa ::1, sin corchetes.');
    }
    hostname = value.toLowerCase();
  }
  hostname ??= '127.0.0.1';
  return { args: [...forwarded, '--hostname', hostname], hostname,
    localOnly: ['127.0.0.1', 'localhost', '::1'].includes(hostname) };
}
