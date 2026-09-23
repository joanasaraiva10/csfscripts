from pathlib import Path
import numpy as np
import jpegio as jio

SRC = Path("/home/kali/deepfish/working/iceberg-02/iceberg.jpg")
OUT = Path("/home/kali/deepfish/results/iceberg-02/y-zigzag-final")
OUT.mkdir(parents=True, exist_ok=True)

j = jio.read(str(SRC))
Y = j.coef_arrays[0].astype(np.int64)

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

bh = Y.shape[0] // 8
bw = Y.shape[1] // 8

def get_block(by,bx):
    return Y[by*8:(by+1)*8, bx*8:(bx+1)*8]

def raster_blocks():
    for by in range(bh):
        for bx in range(bw):
            yield get_block(by,bx)

def mcu_blocks():
    # 4:2:0 => 2x2 Y blocks por MCU
    for my in range(bh//2):
        for mx in range(bw//2):
            yield get_block(2*my+0, 2*mx+0)
            yield get_block(2*my+0, 2*mx+1)
            yield get_block(2*my+1, 2*mx+0)
            yield get_block(2*my+1, 2*mx+1)

def extract(block_iter, mode):
    bits = []

    for block in block_iter():
        for k,(u,v) in enumerate(ZZ):
            c = int(block[u,v])

            if mode == "all":
                pass
            elif mode == "ac":
                if k == 0:
                    continue
            elif mode == "nonzero_ac":
                if k == 0 or c == 0:
                    continue
            elif mode == "jsteg_like":
                if k == 0 or abs(c) <= 1:
                    continue
            else:
                raise ValueError(mode)

            bits.append(c & 1)

    return np.asarray(bits,dtype=np.uint8)

for block_order, block_iter in [
    ("raster", raster_blocks),
    ("mcu", mcu_blocks),
]:
    for mode in [
        "all",
        "ac",
        "nonzero_ac",
        "jsteg_like",
    ]:
        bits = extract(block_iter, mode)

        for bitorder in ("big","little"):
            data = np.packbits(bits, bitorder=bitorder).tobytes()

            name = f"Y_{block_order}_{mode}_{bitorder}.bin"
            (OUT/name).write_bytes(data)

            print(
                name,
                "bits=",len(bits),
                "bytes=",len(data),
                "first16=",data[:16].hex(" ")
            )

print("written:",OUT)
