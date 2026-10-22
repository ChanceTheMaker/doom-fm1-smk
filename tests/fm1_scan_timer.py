"""Compile the real shared-timer ISR with counters; no device access."""
from pathlib import Path
import subprocess,os
root=Path(__file__).resolve().parents[1]
s=(root/'src/native/usb_update.c').read_text();a=s.index('#if DP_SMK\n#define DP_USB_TIMER_PERIOD');b=s.index('void dp_usb_init',a);fragment=s[a:b]
for smk in (0,1):
 code='#include <assert.h>\n#define DP_SMK '+str(smk)+'\nstatic unsigned ticks,scans,polls;void fm1_timer5_ack(void){ticks++;}void dp_input_tick(void){scans++;}void usb_poll(void){polls++;}\n'+fragment+'\nint main(void){for(unsigned i=0;i<10000;i++)dp_usb_irq();assert(ticks==10000);assert(scans=='+('0' if smk else '10000')+');assert(polls=='+('10000' if smk else '2000')+');assert(DP_USB_TIMER_PERIOD=='+('3000' if smk else '600')+');}\n'
 out=root/'build/fm1-timer-tests';out.mkdir(parents=True,exist_ok=True);c=out/('timer'+str(smk)+'.c');exe=c.with_suffix('');c.write_text(code)
 linux=lambda p:subprocess.check_output(['wsl','-e','wslpath','-a',p.as_posix()],text=True).strip()
 if os.name=='nt':cmd=['wsl','-e','cc','-std=c11','-Wall','-Wextra','-Werror',linux(c),'-o',linux(exe)];run=['wsl','-e',linux(exe)]
 else:cmd=['cc','-std=c11','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)];run=[str(exe)]
 subprocess.run(cmd,check=True);subprocess.run(run,check=True)
 print('PASS shared timer: '+('SMK USB unchanged' if smk else 'FM-1 10 kHz input, 2 kHz USB'))
