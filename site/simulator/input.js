// SPDX-License-Identifier: GPL-3.0-only
export const actions=['Turn left','Forward','Turn right','Back','Fire','Use / retry','Menu','Select','Run','Strafe left','Strafe right','Next weapon'];
export const keymap={ArrowLeft:0,KeyA:0,ArrowUp:1,KeyW:1,ArrowRight:2,KeyD:2,ArrowDown:3,KeyS:3,Space:4,KeyF:5,Escape:6,Enter:7,ShiftLeft:8,ShiftRight:8,KeyQ:9,KeyZ:9,KeyE:10,KeyC:10,BracketRight:11,KeyR:11};
// Keyboard + multiple fingers can hold the same action without releasing each other.
export function createInput(send,paint=()=>{}){const owners=new Map(),counts=new Map();
 function release(owner){if(!owners.has(owner))return;const action=owners.get(owner);owners.delete(owner);const n=counts.get(action)-1;if(n)counts.set(action,n);else{counts.delete(action);send(action,false);paint(action,false);}}
 function press(owner,action){if(!Number.isInteger(action)||action<0||action>=actions.length)return;if(owners.get(owner)===action)return;release(owner);owners.set(owner,action);const n=counts.get(action)||0;counts.set(action,n+1);if(!n){send(action,true);paint(action,true);}}
 function clear(){for(const owner of [...owners.keys()])release(owner);}
 return {press,release,clear};}
