"""Compare serialized SQLite commit paths, not task quality or physical computing."""
import json
import platform
import sqlite3
import tempfile
import time
from pathlib import Path
from thermal_substrate import ThermalSubstrate

def measure(call, count):
    samples=[]
    for _ in range(count):
        start=time.perf_counter_ns();call();samples.append(time.perf_counter_ns()-start)
    ordered=sorted(samples)
    return {'operations':count,'mean_us':sum(samples)/count/1000,
            'p95_us':ordered[int(.95*(count-1))]/1000,'throughput_per_second':count/(sum(samples)/1e9)}

def run(count=1000):
    with tempfile.TemporaryDirectory() as root:
        thermal=ThermalSubstrate(str(Path(root)/'thermal.db'));thermal.register_entity('a','benchmark')
        baseline=sqlite3.connect(str(Path(root)/'baseline.db'))
        baseline.execute('CREATE TABLE counters(id TEXT PRIMARY KEY,value REAL)')
        baseline.execute("INSERT INTO counters VALUES ('a',300)");baseline.commit()
        def update():
            baseline.execute('BEGIN IMMEDIATE')
            baseline.execute("UPDATE counters SET value=value+3 WHERE id='a'");baseline.commit()
        result={'python':platform.python_version(),'platform':platform.platform(), 'sqlite':sqlite3.sqlite_version,
                'scope':'single writer, local filesystem, one commit per operation; no quality, cost or distributed-scaling claims',
                'baseline':measure(update,count),'thermal':measure(lambda:thermal.execute_with_coupling('benchmark','a'),count)}
        baseline.close();thermal.close();return result
if __name__=='__main__': print(json.dumps(run(),indent=2))
