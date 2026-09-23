from pathlib import Path
import numpy as np
import jpegio as jio

SRC = Path("/home/kali/deepfish/working/iceberg-02/iceberg.jpg")
OUT = Path("/home/kali/deepfish/results/iceberg-02/recovered-secret.json")

OUT.parent.mkdir(parents=True, exist_ok=True)

ZZ = [
    (0,0),
    (0,1),(1,0),
    (2,0),(1,1),(0,2),
    (0,3),(1,2),(2,1),(3,0),
    (4,0),(3,1),(2,2),(1,3),(0,4),
    (0,5),(1,4),(2,3),(3,2),(4,1),(5,0),
    (6,0),(5,1),(4,2),(3,3),(2,4),(1,5),(0,6),
    (0,7),(1,6),(2,5),(3,4),(4,3),(5,2),(6,1),(7,0),
    (7,1),(6,2),(5,3),(4,4),(3,5),(2,6),(1,7),
    (2,7),(3,6),(4,5),(5,4),(6,3),(7,2),
    (7,3),(6,4),(5,5),(4,6),(3,7),
    (4,7),(5,6),(6,5),(7,4),
    (7,5),(6,6),(5,7),
    (6,7),(7,6),
    (7,7),
]

jpg = jio.read(str(SRC))
Y = jpg.coef_arrays[0].astype(np.int64)

bh = Y.shape[0] // 8
bw = Y.shape[1] // 8

bits = []

for by in range(bh):
    for bx in range(bw):

        block = Y[
            by*8:(by+1)*8,
            bx*8:(bx+1)*8
        ]
        for u,v in ZZ[1:]:

            c = int(block[u,v])

            if abs(c) <= 1:
                continue

            bits.append(c & 1)

bits = np.asarray(bits, dtype=np.uint8)

data = np.packbits(
    bits,
    bitorder="big"
).tobytes()

# primeiros 64 bits = tamanho
size = int.from_bytes(
    data[:8],
    "big"
)

payload = data[8:8+size]

print("hidden length:", size)
print("first bytes:", payload[:32])
print("last bytes :", payload[-32:])

OUT.write_bytes(payload)

print("written:", OUT)
