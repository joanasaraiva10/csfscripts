data = open("polish_cow.webp", "rb").read()

pos = 12                        # skip "RIFF", size, "WEBP"
durs = []
while pos + 8 <= len(data):
    tag  = data[pos:pos+4]
    size = int.from_bytes(data[pos+4:pos+8], "little")
    body = pos + 8
    if tag == b"ANMF":          # a frame
        h = data[body:body+16]  # 16-byte frame header
        durs.append(int.from_bytes(h[12:15], "little"))   # bytes 12-14 = duration
    pos = body + size + (size & 1)   # jump to the next chunk (pad to even)

print(len(durs))
print(durs[:20])

import collections
print(min(durs), max(durs))
print(collections.Counter(durs).most_common(10))
deltas = [d - 50 for d in durs]
print(min(deltas), max(deltas))

import matplotlib.pyplot as plt
plt.hist(deltas, bins=64)
plt.show()

import numpy as np
out = bytes((np.cumsum(deltas) % 256).astype(np.uint8))
print(out[:60])

start = out.find(b"{")
open("message.json", "wb").write(out[start:])

import json
json.load(open("message.json"))    # no error = it's valid JSON