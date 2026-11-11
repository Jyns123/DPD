import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location('container_server', Path(__file__).resolve().parents[2] / 'scripts/container_server.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class DailySchedule(unittest.TestCase):
 def test_same_day_and_next_day_in_lima(self):
  now = datetime(2026, 11, 10, 6, 0, tzinfo=ZoneInfo('America/Lima'))
  self.assertEqual(server.next_refresh(now, '06:30').isoformat(), '2026-11-10T06:30:00-05:00')
  self.assertEqual(server.next_refresh(now, '05:30').isoformat(), '2026-11-11T05:30:00-05:00')

 def test_rejects_invalid_time(self):
  now = datetime(2026, 11, 10, tzinfo=ZoneInfo('America/Lima'))
  for value in ('25:00', '06:60', 'bad', '1:2:3'):
   with self.subTest(value=value), self.assertRaises(ValueError):
    server.next_refresh(now, value)
