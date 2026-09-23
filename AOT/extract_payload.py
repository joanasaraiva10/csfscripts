"""
extract_payload.py - recover the file hidden in the video's pixels.

Usage: python3 extract_payload.py "video.mkv" [out_file] [width height]
"""
import subprocess, sys, math
import numpy as np

path = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "payload.bin"
W = int(sys.argv[3]) if len(sys.argv) > 3 else 854
H = int(sys.argv[4]) if len(sys.argv) > 4 else 480
XS = [53, 159, 266, 373, 480, 586, 693, 800]
YS = [60, 180, 300, 420]
FS = W * H * 3

p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     stdout=subprocess.PIPE, bufsize=FS * 4)
stream = bytearray()
need = None
n = 0
while need is None or len(stream) < need:
    buf = p.stdout.read(FS)
    if len(buf) < FS:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    g = f[np.ix_(YS, XS)] & 1                      # (4, 8, 3)
    bits = g.transpose(2, 0, 1).reshape(-1)        # R plane | G plane | B plane
    stream += np.packbits(bits).tobytes()          # 12 bytes
    n += 1
    if need is None and len(stream) >= 8:
        length = int.from_bytes(stream[:8], "big")
        print(f"header length = {length} bytes  (needs {math.ceil((length + 8) / 12)} frames)")
        if length <= 0 or length > 200_000_000:
            sys.exit("Length looks wrong - the layout assumption doesn't hold for this file.")
        need = 8 + length
    if n % 5000 == 0:
        print(f"  ...{n} frames", file=sys.stderr)
p.kill()

if need is None or len(stream) < need:
    sys.exit(f"Ran out of frames after {n}: have {len(stream)} bytes, need {need}")
data = bytes(stream[8:need])
open(out, "wb").write(data)
print(f"decoded {n} frames -> {len(data)} bytes -> {out}")
print("first bytes:", data[:16])
if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
    riff = int.from_bytes(data[4:8], "little")
    print("WebP header OK; RIFF size field", riff, "->", "matches" if riff + 8 == len(data) else "MISMATCH")