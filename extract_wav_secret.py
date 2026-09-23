import wave
import numpy as np
from pathlib import Path
from PIL import Image
import io

SRC = Path("/home/kali/deepfish/working/wav-01/dj_cara_after_hours.wav")
OUT = Path("/home/kali/deepfish/results/wav-01/lsb-secret")
OUT.mkdir(parents=True, exist_ok=True)

print("[+] Source:", SRC)

with wave.open(str(SRC), "rb") as w:
    channels = w.getnchannels()
    width = w.getsampwidth()
    rate = w.getframerate()
    frames = w.getnframes()

    print("[+] channels:", channels)
    print("[+] sample width:", width)
    print("[+] sample rate:", rate)
    print("[+] frames:", frames)

    if channels != 2 or width != 2:
        raise SystemExit("Esperava WAV PCM 16-bit stereo")

    raw = w.readframes(frames)

samples = np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
u = samples.view(np.uint16)

left_lsb = (u[:, 0] & 1).astype(np.uint8)
right_lsb = (u[:, 1] & 1).astype(np.uint8)

same = np.mean(left_lsb == right_lsb)

print()
print(f"[+] L/R LSB equality: {same*100:.8f}%")


bits = left_lsb

MAGICS = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"BM": "bmp",
    b"II*\x00": "tif",
    b"MM\x00*": "tif",
    b"RIFF": "riff",
    b"PK\x03\x04": "zip",
    b"%PDF-": "pdf",
    b"P5\n": "pgm",
    b"P6\n": "ppm",
}

def scan(data, label):
    found = False

    for magic, ext in MAGICS.items():
        start = 0

        while True:
            pos = data.find(magic, start)

            if pos < 0:
                break

            print(f"[!] {label}: possível {ext} em offset {pos}")
            found = True

            candidate = OUT / f"carved_{label}_{pos}.{ext}"
            candidate.write_bytes(data[pos:])

            try:
                img = Image.open(io.BytesIO(data[pos:]))
                img.load()

                good = OUT / (
                    f"VALID_{label}_{pos}_"
                    f"{img.width}x{img.height}.{img.format.lower()}"
                )

                img.save(good)

                print(
                    f"    >>> IMAGEM VÁLIDA: "
                    f"{img.format} {img.size} -> {good}"
                )

            except Exception:
                pass

            start = pos + 1

    return found


print("\n[+] Testing packed LSB streams...")

for shift in range(8):

    shifted = bits[shift:]

    for order in ("big", "little"):

        packed = np.packbits(
            shifted,
            bitorder=order
        ).tobytes()

        name = f"{order}_shift{shift}"

        path = OUT / f"payload_{name}.bin"
        path.write_bytes(packed)

        scan(packed, name)


        inverted = bytes(b ^ 0xff for b in packed)

        scan(
            inverted,
            f"{name}_inverted"
        )


payload = np.packbits(bits, bitorder="big")

print("\n[+] Creating raw grayscale candidates...")

for width in [
    128, 256, 320, 512, 640,
    800, 1024, 1280, 1600,
    1920, 2048, 2560, 4096
]:
    height = len(payload) // width

    if height < 10:
        continue

    n = width * height

    imgdata = payload[:n].reshape(height, width)

    img = Image.fromarray(
        imgdata.astype(np.uint8),
        mode="L"
    )

    dest = OUT / f"raw_gray_{width}x{height}.png"
    img.save(dest)

    print("[+] wrote", dest)



print("\n[+] Creating raw 1-bit candidates...")

for width in [
    128, 256, 320, 512, 640,
    800, 1024, 1280, 1600,
    1920, 2048, 2560, 4096, 8192
]:
    height = len(bits) // width

    if height < 10:
        continue

    n = width * height

    pixels = (
        bits[:n].reshape(height, width) * 255
    ).astype(np.uint8)

    img = Image.fromarray(pixels, mode="L")

    dest = OUT / f"raw_bits_{width}x{height}.png"
    img.save(dest)

    print("[+] wrote", dest)

print()
print("[+] DONE")
print("[+] Results:", OUT)
