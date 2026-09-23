"""
Reads the first 8 bytes as a big-endian length prefix, then extracts exactly
that many payload bytes that follow.

Usage:
    python extract_full_cyclic.py
"""

import struct
import numpy as np
from PIL import Image
from gijswijt_cyclic import gijswijt_positions_cyclic

IMAGE_PATH = "reconstructed.png"
HEADER_BYTES = 8

img = Image.open(IMAGE_PATH).convert("RGB")
rgb8 = np.array(img)
print("Loaded shape (H, W, C):", rgb8.shape)

flat = rgb8.reshape(-1)
lsbs = flat & 1
n = len(lsbs)

def pack_msb(bits):
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        b = 0
        for bit in bits[i:i + 8]:
            b = (b << 1) | bit
        out.append(b)
    return bytes(out)

header_positions = gijswijt_positions_cyclic(HEADER_BYTES * 8)
header_bits = [int(lsbs[p]) for p in header_positions]
header_bytes = pack_msb(header_bits)
payload_len = struct.unpack(">Q", header_bytes)[0]
print(f"Header bytes: {header_bytes!r}")
print(f"Parsed payload length: {payload_len} bytes")

if payload_len <= 0 or payload_len > 2_000_000:
    print("\nWARNING: parsed length looks implausible. Stopping before a huge/slow extraction.")
else:
    total_bytes = HEADER_BYTES + payload_len
    total_positions_needed = total_bytes * 8
    positions = gijswijt_positions_cyclic(total_positions_needed)
    positions = [p for p in positions if p < n]
    bits = [int(lsbs[p]) for p in positions]
    all_bytes = pack_msb(bits)

    payload = all_bytes[HEADER_BYTES:HEADER_BYTES + payload_len]

    with open("hidden_payload.bin", "wb") as f:
        f.write(payload)
    print(f"\nWrote {len(payload)} bytes to hidden_payload.bin")

    try:
        text = payload.decode("utf-8")
        print("\n--- Decoded payload (UTF-8) ---")
        print(text)
        with open("hidden_script.py", "w", encoding="utf-8") as f:
            f.write(text)
        print("\nAlso saved as hidden_script.py (since it decoded cleanly as text).")
    except UnicodeDecodeError as e:
        print(f"\nPayload is not clean UTF-8 text ({e}).")
        print("Raw bytes (repr):")
        print(payload)
