import math
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from thermal_substrate.core import ThermalSubstrate

class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name)/'state.sqlite')
        self.system = ThermalSubstrate(self.path)
    def tearDown(self):
        self.system.close()
        self.tmp.cleanup()
    def state(self, entity):
        return self.system.db.execute('SELECT temperature,entropy,energy,phase FROM thermal_entities WHERE entity_id=?',(entity,)).fetchone()
    def test_transfer_preserves_requested_identity_and_temperature_sum(self):
        self.system.register_entity('z','test',800)
        self.system.register_entity('a','test',200)
        self.assertEqual(self.system.heat_transfer('z','a',1),600)
        self.assertEqual(self.state('z')[0],500)
        self.assertEqual(self.state('a')[0],500)
        for key in ['z','a']:
            temperature,entropy,energy,phase=self.state(key)
            self.assertAlmostEqual(energy,temperature*entropy)
            self.assertEqual(phase,'liquid')
    def test_invalid_numbers_leave_state_unchanged(self):
        for bad in [float('nan'),float('inf'),-1,True,'300']:
            with self.assertRaises(ValueError): self.system.register_entity('bad','test',bad)
        self.system.register_entity('a','test')
        for bad in [-1,1.1,float('nan')]:
            with self.assertRaises(ValueError): self.system.heat_transfer('a','b',bad)
        self.assertEqual(self.state('a')[0],300)
    def test_zero_is_active_and_finite_extremes_do_not_overflow(self):
        self.system.register_entity('zero','test',0)
        self.assertIn('FROZEN',self.system.get_system_state_prompt())
        self.system.register_entity('large','test',1e308)
        self.system.heat_transfer('large','zero',1)
        self.assertTrue(math.isfinite(self.state('large')[0]))
        self.assertIn('PLASMA',self.system.get_system_state_prompt())
    def test_concurrent_updates_have_no_loss_and_survive_reopen(self):
        self.system.register_entity('a','test',300)
        second=ThermalSubstrate(self.path)
        try:
            with ThreadPoolExecutor(max_workers=8) as workers:
                list(workers.map(lambda i: (self.system if i%2 else second).execute_with_coupling('op','a'),range(100)))
        finally: second.close()
        self.assertEqual(self.state('a')[0],600)
        self.assertEqual(self.state('a')[3],'gas')
        self.system.close()
        self.system=ThermalSubstrate(self.path)
        self.assertEqual(self.state('a')[0],600)
        self.system.cool_down()
        self.assertEqual(self.state('a')[0],570)
