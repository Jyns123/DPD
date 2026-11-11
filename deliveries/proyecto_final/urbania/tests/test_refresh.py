import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('refresh_data', Path(__file__).resolve().parents[2] / 'scripts/refresh_data.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class Refresh(unittest.TestCase):
 def test_runs_all_steps_in_order(self):
  with tempfile.TemporaryDirectory() as folder, patch.object(refresh, 'ROOT', Path(folder)), patch.object(refresh.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as run:
   (Path(folder) / 'data/urbania').mkdir(parents=True)
   (Path(folder) / 'data/catalog.json').write_text('{}')
   self.assertEqual(refresh.main(), 0)
   self.assertEqual((Path(folder) / 'data/catalog-published.json').read_text(), '{}')
   self.assertEqual([call.args[0][1] for call in run.call_args_list], ['urbania/update.py', 'analytics/prepare_data.py', 'analytics/validate_data.py'])

 def test_stops_after_failed_capture(self):
  with tempfile.TemporaryDirectory() as folder, patch.object(refresh, 'ROOT', Path(folder)), patch.object(refresh.subprocess, 'run', return_value=SimpleNamespace(returncode=2)) as run:
   self.assertEqual(refresh.main(), 2)
   self.assertEqual(run.call_count, 1)

 def test_concurrent_pipeline_is_skipped(self):
  with tempfile.TemporaryDirectory() as folder, patch.object(refresh, 'ROOT', Path(folder)):
   root = Path(folder) / 'data/urbania'
   root.mkdir(parents=True)
   with (root / 'refresh.lock').open('a+b') as lock, patch.object(refresh.subprocess, 'run') as run:
    self.assertTrue(refresh.acquire_lock(lock))
    self.assertEqual(refresh.main(), 3)
    run.assert_not_called()
