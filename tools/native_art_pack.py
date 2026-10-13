# SPDX-License-Identifier: GPL-3.0-only
"""Lossless pruning for the fixed native campaign (not arbitrary user WADs)."""
import re
import struct


def texture_subset(rows, engine):
    lumps = dict(rows)
    needed = {'SKY1', 'SKY2', 'SKY3'}
    for name, data in rows:
        if name == 'SIDEDEFS':
            needed.update(data[i+j:i+j+8].rstrip(b'\0').decode()
                          for i in range(0, len(data), 30) for j in (4, 12, 20))
    switches = re.findall(r'\{\s*"(SW[12][A-Z0-9]+)"\s*,\s*"(SW[12][A-Z0-9]+)"',
                          (engine/'p_switch.c').read_text())
    for pair in switches:
        if needed.intersection(pair):
            needed.update(pair)
    data = lumps['TEXTURE1']
    records = []
    for i in range(struct.unpack_from('<I', data)[0]):
        off = struct.unpack_from('<I', data, 4+4*i)[0]
        count = struct.unpack_from('<H', data, off+20)[0]
        records.append((data[off:off+8].rstrip(b'\0').decode(), data[off:off+22+10*count]))
    # Preserve the whole animation cycle when any member is used.
    names = [name for name, _ in records]
    for end, start in re.findall(r'\{true,\s*"([A-Z0-9]+)"\s*,\s*"([A-Z0-9]+)"',
                                 (engine/'p_spec.c').read_text()):
        if start in names and end in names:
            cycle = names[names.index(start):names.index(end)+1]
            if needed.intersection(cycle):
                needed.update(cycle)
    # Index zero is the engine's "no texture" sentinel, so keep its old entry.
    needed.add(names[0])
    records = [record for name, record in records if name in needed]
    packed = bytearray(struct.pack('<I', len(records)) + bytes(4*len(records)))
    for i, record in enumerate(records):
        struct.pack_into('<I', packed, 4+4*i, len(packed))
        packed.extend(record)
    return bytes(packed)


def compact_patch(data):
    """Alias identical column streams; preserve every pixel and patch origin."""
    w, h = struct.unpack_from('<HH', data)
    if not 0 < w <= 1024 or not 0 < h < 255:
        raise ValueError('Unsupported patch dimensions')
    result = bytearray(data[:8] + bytes(4*w))
    seen = {}
    for x in range(w):
        start = pos = struct.unpack_from('<I', data, 8+4*x)[0]
        while data[pos] != 255:
            pos += data[pos+1]+4
        column = data[start:pos+1]
        if column not in seen:
            seen[column] = len(result)
            result.extend(column)
        struct.pack_into('<I', result, 8+4*x, seen[column])
    return bytes(result)


def scale_patch(data, xnum, xden, ynum, yden):
    """Nearest-neighbour asset compilation to the physical LCD pixel budget."""
    w, h, left, top = struct.unpack_from('<hhhh', data)
    nw, nh = max(1, (w*xnum+xden-1)//xden), max(1, (h*ynum+yden-1)//yden)
    out = bytearray(struct.pack('<hhhh', nw, nh, left*xnum//xden, top*ynum//yden)+bytes(nw*4))
    for x in range(nw):
        sx = min(w-1, x*xden//xnum)
        col = [-1]*h
        pos = struct.unpack_from('<I', data, 8+4*sx)[0]
        while data[pos] != 255:
            y, n = data[pos], data[pos+1]
            col[y:y+n] = data[pos+3:pos+3+n]
            pos += n+4
        samples = [col[min(h-1, y*yden//ynum)] for y in range(nh)]
        struct.pack_into('<I', out, 8+4*x, len(out))
        y = 0
        while y < nh:
            if samples[y] < 0:
                y += 1
                continue
            first = y
            while y < nh and samples[y] >= 0:
                y += 1
            out.extend(bytes([first, y-first, 0, *samples[first:y], 0]))
        out.append(255)
    return compact_patch(bytes(out))
