"""blackpix.py - list the non-black pixels inside (nearly) black frames.
Usage: python3 blackpix.py "video.mkv" START END [W H]
Prints, per frame: how many non-zero sub-pixels, their (x,y,channel)=value, and saves
blackpix_<frame>.png"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageFilter
path, s, e = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
W = int(sys.argv[4]) if len(sys.argv) > 4 else 854
H = int(sys.argv[5]) if len(sys.argv) > 5 else 480
cmd = ["ffmpeg","-v","error","-i",path,"-map","0:v:0","-vf",f"select='between(n,{s},{e})'",
       "-fps_mode","passthrough","-f","rawvideo","-pix_fmt","rgb24","-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
n = s
while True:
    b = p.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    ys, xs, cs = np.nonzero(f)
    print(f"frame {n}: {len(ys)} non-zero sub-pixels; max value {f.max()}")
    for y, x, c in list(zip(ys, xs, cs))[:40]:
        print(f"    x={x:4d} y={y:3d} ch={'RGB'[c]} val={f[y,x,c]}")
    img = Image.fromarray(((f > 0) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
    img.save(f"blackpix_{n}.png")
    n += 1