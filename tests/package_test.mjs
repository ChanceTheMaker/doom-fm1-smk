// SPDX-License-Identifier: GPL-3.0-only
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {parsePackage} from '../web/vendor/smk37-update.js';
const base = new URL('../build/try-smk-pro/site/', import.meta.url);
const m = JSON.parse(await readFile(new URL('candidate.json', base), 'utf8'));
const b = new Uint8Array(await readFile(new URL(m.package, base)));
const p = await parsePackage(b, m.sha256);
assert.equal(p.product, 'SMK-37_991');
assert.equal(p.version, 'DOOM SMK TEST02');
assert.equal(p.format, 1);
await assert.rejects(parsePackage(b, '0'.repeat(64)), /reviewed candidate/);
await assert.rejects(parsePackage(b.subarray(1), m.sha256), /size/);
for (const at of [40, 1024, b.length-1]) {
  const damaged = b.slice(); damaged[at] ^= 1;
  await assert.rejects(parsePackage(damaged, m.sha256), /checksum/);
}
console.log('PASS: staged package identity/hash/CRCs; wrong hash, truncation and corruption rejected.');
