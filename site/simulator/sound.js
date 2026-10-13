// SPDX-License-Identifier: GPL-3.0-only
// Bounded mono queue; convert the device's 44.1 kHz effects to the output rate.
class DoomSound extends AudioWorkletProcessor {
 constructor(){super();this.buffer=new Float32Array(16384);this.read=0;this.count=0;this.phase=0;this.primed=false;this.port.onmessage=({data})=>{if(data.clear){this.read=this.count=this.phase=0;this.primed=false;return;}if(!(data instanceof Float32Array))return;for(const v of data){if(this.count>=this.buffer.length){this.read=(this.read+1)%this.buffer.length;this.count--;}this.buffer[(this.read+this.count++)%this.buffer.length]=v;}};}
 process(inputs,outputs){const out=outputs[0];if(!out.length)return true;if(!this.primed&&this.count>=2520)this.primed=true;
 for(let i=0;i<out[0].length;i++){let v=0;if(this.primed&&this.count>1){const a=this.buffer[this.read],b=this.buffer[(this.read+1)%this.buffer.length];v=a+(b-a)*this.phase;this.phase+=44100/sampleRate;const n=Math.floor(this.phase);this.phase-=n;this.read=(this.read+n)%this.buffer.length;this.count=Math.max(0,this.count-n);}else{this.primed=false;this.phase=0;}for(const ch of out)ch[i]=v;}return true;}
}
registerProcessor('doom-sound',DoomSound);
