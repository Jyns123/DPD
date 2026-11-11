"""Actualiza Urbania, prepara el catálogo y valida bajo un único candado."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'urbania'))
from update import acquire_lock  # noqa: E402


def main():
    db = ROOT / 'data/urbania/urbania.sqlite'
    db.parent.mkdir(parents=True, exist_ok=True)
    with (db.parent / 'refresh.lock').open('a+b') as lock:
        if not acquire_lock(lock):
            print('Otra actualización del catálogo está en curso.', file=sys.stderr)
            return 3
        for args in [
            ['urbania/update.py', '--db', str(db), '--out', str(db.parent / 'urbania_actual.csv')],
            ['analytics/prepare_data.py'],
            ['analytics/validate_data.py'],
        ]:
            result = subprocess.run([sys.executable, *args], cwd=ROOT, check=False)
            if result.returncode:
                return result.returncode
        # El servidor solo lee la versión publicada después de la validación.
        source = ROOT / 'data/catalog.json'
        target = ROOT / 'data/catalog-published.json'
        temporary = target.with_suffix('.json.tmp')
        try:
            shutil.copyfile(source, temporary)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
