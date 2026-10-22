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
pad_values=[150,222,0xc000,0x96c707,124,0,219|(224<<16),0]
wire=[0xf0,0x7d,0x44,0x50,2]+[(v>>s)&127 for v in pad_values for s in range(0,35,7)]
wire += [(-sum(wire[1:]))&127,0xf7]
assert list(decode(wire,True).values())==pad_values
assert decode(wire) is None
assert decode(wire[:-1],True) is None
wire[8]^=1
try:decode(wire,True)
except ValueError:pass
else:raise AssertionError('Corrupt pad diagnostic accepted')
print('PASS pad status decoding: isolated message type, full-width fields and checksum refusal; no device I/O')
for message in (b'', b'OBJ S29 F8 N0 T188', b'GUN S9 F32768 N0'):
    payload=message.ljust(32,b'\0')
    values=[int.from_bytes(payload[i:i+4],'little') for i in range(0,32,4)]
    wire=[0xf0,0x7d,0x44,0x50,3]+[(v>>s)&127 for v in values for s in range(0,35,7)]
    wire += [(-sum(wire[1:]))&127,0xf7]
    assert decode(wire,error=True)=={'error':message.decode('ascii')}
    assert decode(wire) is None and decode(wire,pads=True) is None
    assert decode(wire[:-1],error=True) is None
    wire[8]^=1
    try:decode(wire,error=True)
    except ValueError:pass
    else:raise AssertionError('Corrupt stop reason accepted')
print('PASS stop reason decoding: healthy empty response, exact text, isolated type and checksum refusal; no device I/O')

perf_values=[1234,35,10000,1234567,300,0,1,0]
wire=[0xf0,0x7d,0x44,0x50,4]+[(v>>s)&127 for v in perf_values for s in range(0,35,7)]
wire += [(-sum(wire[1:]))&127,0xf7]
assert list(decode(wire,performance=True).values())==perf_values
assert decode(wire) is None and decode(wire,pads=True) is None
wire[8]^=1
try:decode(wire,performance=True)
except ValueError:pass
else:raise AssertionError('Corrupt performance diagnostic accepted')
print('PASS FM-1 performance counters: isolated type and checksum refusal')
