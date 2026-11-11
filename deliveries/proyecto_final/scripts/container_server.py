"""Ejecuta Next.js y programa una actualización diaria dentro del mismo contenedor."""
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def next_refresh(now, configured):
    try:
        hour, minute = map(int, configured.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError()
    except ValueError:
        raise ValueError('REFRESH_TIME debe tener el formato HH:MM (00:00 a 23:59).') from None
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return target if target > now else target + timedelta(days=1)


def main():
    enabled = os.environ.get('REFRESH_ENABLED', 'true').lower() in {'true', '1', 'yes'}
    zone = ZoneInfo('America/Lima')
    scheduled = next_refresh(datetime.now(zone), os.environ.get('REFRESH_TIME', '06:30')) if enabled else None
    server = subprocess.Popen(['node', 'scripts/start-local.mjs', 'start', '--hostname', '0.0.0.0'], start_new_session=True)
    refresh = None
    stopping = False

    def stop(_signal, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    if scheduled:
        print(f'Próxima actualización de Urbania: {scheduled.isoformat()}', flush=True)
    else:
        print('Actualización automática de Urbania desactivada.', flush=True)
    try:
        while not stopping and server.poll() is None:
            now = datetime.now(zone)
            if refresh is not None and refresh.poll() is not None:
                print(f'Actualización de Urbania terminó con código {refresh.returncode}.', flush=True)
                refresh = None
            if scheduled and now >= scheduled:
                if refresh is None:
                    print('Iniciando actualización de Urbania.', flush=True)
                    refresh = subprocess.Popen([sys.executable, 'scripts/refresh_data.py'], start_new_session=True)
                else:
                    print('Actualización anterior aún en curso; se omite esta ejecución.', flush=True)
                scheduled = next_refresh(now, os.environ.get('REFRESH_TIME', '06:30'))
                print(f'Próxima actualización de Urbania: {scheduled.isoformat()}', flush=True)
            time.sleep(1)
    finally:
        for process in (server, refresh):
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        for process in (server, refresh):
            if process is not None and process.poll() is None:
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
    return server.returncode if not stopping and server.returncode else 0


if __name__ == '__main__':
    raise SystemExit(main())
