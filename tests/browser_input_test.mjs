import assert from 'node:assert/strict';
import {createInput,keymap} from '../site/simulator/input.js';
const events=[];const i=createInput((a,d)=>events.push([a,d]));
i.press('keyboard',4);i.press('finger',4);i.release('keyboard');assert.deepEqual(events,[[4,true]]);i.release('finger');assert.deepEqual(events,[[4,true],[4,false]]);
events.length=0;i.press('finger',1);i.press('finger',1);i.press('finger',2);i.press('second',4);i.clear();assert.deepEqual(events,[[1,true],[1,false],[2,true],[4,true],[2,false],[4,false]]);
i.press('bad',undefined);i.press('bad',12);i.release('missing');assert.equal(events.length,6);
assert.equal(keymap.Space,4);assert.equal(keymap.KeyF,5);assert.equal(keymap.Escape,6);assert.equal(keymap.Enter,7);assert.equal(keymap.ShiftLeft,keymap.ShiftRight);
console.log('Input ownership, drag transitions, release-all and keyboard mappings passed.');
