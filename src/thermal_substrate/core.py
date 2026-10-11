"""Persistent thermal heuristic. Temperature is model state, not physical heat."""
import math
import random
import sqlite3
import threading
import time
from contextlib import contextmanager


class ThermalSubstrate:
    def __init__(self, db_path='thermal.db'):
        self._lock = threading.RLock()
        self.db = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
        self._init_schema()

    @contextmanager
    def _transaction(self):
        with self._lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                yield
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise

    def _init_schema(self):
        with self._transaction():
            self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_entities (
                entity_id TEXT PRIMARY KEY, entity_type TEXT, temperature REAL,
                entropy REAL, energy REAL, last_interaction REAL, decay_rate REAL, phase TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id TEXT,
                event_type TEXT, energy_delta REAL, timestamp REAL)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_coupling (
                entity_a TEXT, entity_b TEXT, conductivity REAL, last_transfer REAL,
                PRIMARY KEY (entity_a, entity_b))''')

    @staticmethod
    def _finite(value, name, maximum=None):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'{name} must be a finite nonnegative number')
        if not math.isfinite(value) or value < 0 or (maximum is not None and value > maximum):
            raise ValueError(f'{name} is outside its finite range')
        return float(value)

    def register_entity(self, entity_id, entity_type, initial_temp=300):
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise ValueError('entity_id must be nonempty')
        temperature = self._finite(initial_temp, 'temperature')
        entropy = random.uniform(0.1, 1.0)
        with self._transaction():
            self.db.execute('INSERT OR REPLACE INTO thermal_entities VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (entity_id, entity_type, temperature, entropy, temperature * entropy,
                 time.time(), 0.95, self._determine_phase(temperature)))

    @staticmethod
    def _determine_phase(temperature):
        if temperature > 1000: return 'plasma'
        if temperature > 500: return 'gas'
        if temperature > 273: return 'liquid'
        if temperature > 100: return 'solid'
        return 'frozen'

    def _set_temperature(self, entity_id, temperature):
        temperature = self._finite(temperature, 'temperature')
        self.db.execute('''UPDATE thermal_entities SET temperature=?, energy=? * entropy,
            phase=?, last_interaction=? WHERE entity_id=?''',
            (temperature, temperature, self._determine_phase(temperature), time.time(), entity_id))

    def execute_with_coupling(self, operation, entity_id):
        with self._transaction():
            row = self.db.execute('SELECT temperature, entropy FROM thermal_entities WHERE entity_id=?',
                                  (entity_id,)).fetchone()
            if row is None:
                return None
            temp, entropy = row
            coefficient = temp / 500.0
            result = {'operation':operation, 'phase_coefficient':coefficient,
                      'entropy':entropy, 'phase':self._determine_phase(temp),
                      'throttled':coefficient > 2.0, 'locked':coefficient < 0.4}
            self._set_temperature(entity_id, temp + (1 if result['throttled'] else 3))
            return result

    def heat_transfer(self, entity_a, entity_b, conductivity=0.3):
        conductivity = self._finite(conductivity, 'conductivity', 1.0)
        if entity_a == entity_b:
            return 0
        with self._transaction():
            rows = dict(self.db.execute('SELECT entity_id, temperature FROM thermal_entities WHERE entity_id IN (?, ?)',
                                       (entity_a, entity_b)).fetchall())
            if len(rows) != 2:
                return 0
            temp_a, temp_b = rows[entity_a], rows[entity_b]
            # Scale first to avoid overflow at finite numerical extremes.
            transfer = conductivity * (temp_a * 0.5 - temp_b * 0.5)
            self._set_temperature(entity_a, temp_a - transfer)
            self._set_temperature(entity_b, temp_b + transfer)
            return transfer * 2

    def cool_down(self):
        with self._transaction():
            rows = self.db.execute('SELECT entity_id, temperature, decay_rate FROM thermal_entities').fetchall()
            for entity_id, temperature, decay in rows:
                self._finite(decay, 'decay_rate', 1.0)
                self._set_temperature(entity_id, temperature * decay)

    def get_system_state_prompt(self):
        with self._lock:
            rows = self.db.execute('SELECT temperature, entropy FROM thermal_entities').fetchall()
        if not rows:
            return '[THERMAL STATE: System inactive]'
        count = len(rows)
        avg_temp = math.fsum(t / count for t, _ in rows)
        avg_entropy = math.fsum(e / count for _, e in rows)
        return (f'[THERMAL SYSTEM STATE]\nTemperature: {avg_temp:.0f}K\n'
                f'Phase: {self._determine_phase(avg_temp).upper()}\nEntropy: {avg_entropy:.2f}\n\n'
                'Your operations generate heat. Choose strategically to manage thermal load.')

    def close(self):
        with self._lock:
            self.db.close()
