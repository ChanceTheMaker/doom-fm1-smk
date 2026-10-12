from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from read_runtime_status import decode
values=[2,1,500,501,0,0,0,0xffffffff]
wire=[0xf0,0x7d,0x44,0x50,1]+[(v>>s)&127 for v in values for s in range(0,35,7)]
wire += [(-sum(wire[1:]))&127,0xf7]
assert list(decode(wire).values())==values
assert decode(wire[:-1]) is None
wire[8]^=1
try:decode(wire)
except ValueError:pass
else:raise AssertionError('Corrupt diagnostic accepted')
print('PASS runtime status decoding: exact frame, full-width counters and checksum refusal; no device I/O')
