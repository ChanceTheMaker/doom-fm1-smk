import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fm1NoteActions} from '../site/simulator/fm1-controls.js';
const header=fs.readFileSync(new URL('../src/native/fm1_doom_controls.h',import.meta.url),'utf8');
const native=header.match(/dp_fm1_note_actions\[27\]=\{([^}]+)\}/)[1].trim().split(',').map(Number);
assert.deepEqual(fm1NoteActions,native);
assert.equal(fm1NoteActions[24],5);assert.equal(fm1NoteActions[26],4);
assert.equal(fm1NoteActions[11],6);assert.equal(fm1NoteActions[12],7);
console.log('Firmware and simulator use the same FM-1 control layout');
