#!/usr/bin/env python3
"""Read Doom core/audio counters over USB MIDI. Never enters an updater or writes flash."""
import argparse,json,sys,time
from pathlib import Path

QUERY=[0xf0,0x7d,0x44,0x50,1,0xf7]
FIELDS=['active_cores','audio_core_id','audio_blocks','worker_jobs','missed_deadlines','worker_faults','rejected_requests','max_job_ticks']
FM1_FIELDS=['milliseconds','frames','scan_ticks','scan_cost_ticks','max_scan_ticks','actions','light_updates','lcd_timeouts']
PAD_FIELDS=['brightness','fader2_raw','pads_held_and_pressed','last_light_state','light_writes','brightness_changes','fader2_min_max','light_errors']
def decode(wire,pads=False,error=False,performance=False):
    if len(wire)!=47 or wire[:5]!=[0xf0,0x7d,0x44,0x50,4 if performance else 3 if error else 2 if pads else 1] or wire[-1]!=0xf7:return None
    if any(x>127 for x in wire[1:-1]) or sum(wire[1:-1])&127:raise ValueError('Invalid diagnostic checksum')
    values=[sum(wire[5+i*5+j]<<(j*7) for j in range(5)) for i in range(8)]
    if any(v>0xffffffff for v in values):raise ValueError('Invalid diagnostic word')
    if error:return {'error':b''.join(v.to_bytes(4,'little') for v in values).split(b'\0')[0].decode('ascii','replace')}
    return dict(zip(FM1_FIELDS if performance else PAD_FIELDS if pads else FIELDS,values))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--samples',type=int,default=2)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--fm1-performance',action='store_true',help='Read FM-1 frame and matrix-scan counters')
    mode.add_argument('--pads',action='store_true',help='Read SMK pad and brightness state')
    mode.add_argument('--error',action='store_true',help='Read stop reason; empty while running');a=p.parse_args()
    if not 1<=a.samples<=10:p.error('Use 1..10 samples')
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'build/recovery-python'))
    import rtmidi
    inp,out=rtmidi.MidiIn(),rtmidi.MidiOut()
    ins=[i for i,n in enumerate(inp.get_ports()) if n.casefold().strip().startswith('doom') and 'update' not in n.casefold()]
    outs=[i for i,n in enumerate(out.get_ports()) if n.casefold().strip().startswith('doom') and 'update' not in n.casefold()]
    if len(ins)!=1 or len(outs)!=1:raise SystemExit('Expected exactly one running Doom input/output; no query sent')
    inp.ignore_types(sysex=False,timing=True,active_sense=True);inp.open_port(ins[0]);out.open_port(outs[0])
    results=[]
    try:
        for sample in range(a.samples):
            if sample:time.sleep(.5)
            query=QUERY.copy();query[4]=4 if a.fm1_performance else 3 if a.error else 2 if a.pads else 1
            out.send_message(query);deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                message=inp.get_message()
                if not message:time.sleep(.01);continue
                status=decode(message[0],a.pads,a.error,a.fm1_performance)
                if status:
                    if a.pads:
                        status['fader2_min']=status['fader2_min_max']&65535
                        status['fader2_max']=status['fader2_min_max']>>16
                    elif not a.error and not a.fm1_performance:status['max_job_us']=round(status['max_job_ticks']/24,2)
                    results.append(status);break
            else:raise SystemExit('No diagnostic response; no update or flash command was sent')
    finally:inp.close_port();out.close_port()
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
