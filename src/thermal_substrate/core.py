"""Core thermodynamic substrate implementation"""
import sqlite3
import time
import json
import numpy as np

class ThermalSubstrate:
    """
    Thermodynamic computing substrate where entities have thermal properties
    that mathematically couple to execution behavior.
    """
    
    def __init__(self, db_path='thermal.db'):
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize thermal state tables"""
        self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_entities (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT,
            temperature REAL,
            entropy REAL,
            energy REAL,
            last_interaction REAL,
            decay_rate REAL,
            phase TEXT
        )''')
        
        self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT,
            event_type TEXT,
            energy_delta REAL,
            timestamp REAL
        )''')
        
        self.db.execute('''CREATE TABLE IF NOT EXISTS thermal_coupling (
            entity_a TEXT,
            entity_b TEXT,
            conductivity REAL,
            last_transfer REAL,
            PRIMARY KEY (entity_a, entity_b)
        )''')
        
        self.db.commit()
    
    def register_entity(self, entity_id, entity_type, initial_temp=300):
        """Register a new thermal entity"""
        entropy = np.random.uniform(0.1, 1.0)
        energy = initial_temp * entropy
        phase = self._determine_phase(initial_temp)
        
        self.db.execute(
            'INSERT OR REPLACE INTO thermal_entities VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (entity_id, entity_type, initial_temp, entropy, energy, 
             time.time(), 0.95, phase))
        self.db.commit()
    
    def _determine_phase(self, temperature):
        """Determine phase from temperature"""
        if temperature > 1000: return 'plasma'
        if temperature > 500: return 'gas'
        if temperature > 273: return 'liquid'
        if temperature > 100: return 'solid'
        return 'frozen'
    
    def execute_with_coupling(self, operation, entity_id):
        """Execute operation with thermal coupling"""
        cursor = self.db.execute(
            'SELECT temperature, entropy, phase FROM thermal_entities WHERE entity_id=?',
            (entity_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        temp, entropy, phase = row
        phase_coeff = temp / 500.0
        
        # Mathematical coupling
        result = {
            'operation': operation,
            'phase_coefficient': phase_coeff,
            'entropy': entropy,
            'phase': phase,
            'throttled': phase_coeff > 2.0,
            'locked': phase_coeff < 0.4
        }
        
        # Generate heat
        energy_cost = 30 if not result['throttled'] else 10
        new_temp = temp + energy_cost * 0.1
        
        self.db.execute(
            'UPDATE thermal_entities SET temperature=? WHERE entity_id=?',
            (new_temp, entity_id))
        self.db.commit()
        
        return result
    
    def heat_transfer(self, entity_a, entity_b, conductivity=0.3):
        """Transfer heat between entities"""
        cursor = self.db.execute(
            'SELECT temperature FROM thermal_entities WHERE entity_id IN (?, ?)',
            (entity_a, entity_b))
        temps = cursor.fetchall()
        
        if len(temps) != 2:
            return 0
        
        temp_a, temp_b = temps[0][0], temps[1][0]
        heat_flow = conductivity * (temp_a - temp_b)
        
        new_temp_a = temp_a - heat_flow * 0.5
        new_temp_b = temp_b + heat_flow * 0.5
        
        self.db.execute('UPDATE thermal_entities SET temperature=? WHERE entity_id=?',
                       (new_temp_a, entity_a))
        self.db.execute('UPDATE thermal_entities SET temperature=? WHERE entity_id=?',
                       (new_temp_b, entity_b))
        self.db.commit()
        
        return heat_flow
    
    def cool_down(self):
        """Apply passive cooling to all entities"""
        self.db.execute('UPDATE thermal_entities SET temperature = temperature * decay_rate')
        self.db.commit()
    
    def get_system_state_prompt(self):
        """Generate thermal state for AI reflection"""
        cursor = self.db.execute('SELECT AVG(temperature), AVG(entropy) FROM thermal_entities')
        avg_temp, avg_entropy = cursor.fetchone()
        
        if not avg_temp:
            return "[THERMAL STATE: System inactive]"
        
        phase = self._determine_phase(avg_temp)
        
        return f"""[THERMAL SYSTEM STATE]
Temperature: {avg_temp:.0f}K
Phase: {phase.upper()}
Entropy: {avg_entropy:.2f}

Your operations generate heat. Choose strategically to manage thermal load."""
