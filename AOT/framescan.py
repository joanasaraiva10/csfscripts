"""
framescan.py - scan EVERY frame of a lossless RGB video for anomalies.

Usage:  python3 framescan.py "video.mkv" [width height]   (defaults 854 480)
Output: framescan.csv (one row per frame) + a ranked summary on screen.
"""
import subprocess, sys
import numpy as np

path = sys.argv[1]
W = int(sys.argv[2]) if len(sys.argv) > 2 else 854
H = int(sys.argv[3]) if len(sys.argv) > 3 else 480
FS = W * H * 3

cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=FS * 4)

rows = []
prev = None
n = 0
while True:
    buf = p.stdout.read(FS)
    if len(buf) < FS:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    hi = f >> 1
    lsb = f & 1
    flat = (hi[:, :-1] == hi[:, 1:])[:-1] & (hi[:-1, :] == hi[1:, :])[:, :-1]
    flips = (lsb[:, :-1] != lsb[:, 1:])[:-1]
    nflat = int(flat.sum())
    lsb_flat = float((flips & flat).sum() / nflat) if nflat else 0.0
    dprev = float(np.abs(f.astype(np.int16) - prev).mean()) if prev is not None else 0.0
    rows.append((n, round(n * 1001 / 24000, 3), lsb_flat, float(lsb.mean()),
                 dprev, int(np.unique(f).size), nflat / flat.size))
    prev = f.astype(np.int16)
    n += 1
    if n % 2000 == 0:
        print(f"  ...{n} frames", file=sys.stderr)
p.wait()

with open("framescan.csv", "w") as o:
    o.write("frame,time_s,lsb_flat,lsb_mean,diff_prev,uniq_vals,flat_frac\n")
    for r in rows:
        o.write(",".join(str(x) for x in r) + "\n")

a = np.array(rows)
print(f"\n{n} frames scanned -> framescan.csv")


def show(title, col, k=10, largest=True, fmt="{:.4f}"):
    idx = np.argsort(a[:, col])
    idx = idx[::-1][:k] if largest else idx[:k]
    print(f"\n{title}")
    for i in idx:
        r = a[i]
        print(f"  frame {int(r[0]):6d}  t={int(r[1])//60:02d}:{r[1]%60:06.3f}  value=" + fmt.format(r[col]))


med = np.median(a[:, 2])
print(f"median lsb_flat = {med:.4f}   (values near 0.5 on many frames => suspicious)")
show("Highest lsb_flat  (frames whose flat areas have noisy LSBs = likely payload)", 2)
show("Highest lsb_mean  ", 3)
show("Biggest jump from previous frame (inserted frames / scene cuts)", 4, fmt="{:.2f}")
show("Fewest distinct pixel values (synthetic frames: QR code, text, flat colour)", 5, largest=False, fmt="{:.0f}")
print("\nTip: extract any frame N you like with:")
print('  ffmpeg -i "$f" -vf "select=eq(n\\,N)" -vframes 1 -update 1 out.png')