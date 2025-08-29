from PIL import Image
import numpy as np, zlib, sys

cover_path = "qrng.png"
secret_path = "secret.txt"
stego_path  = "stego.png"

img = Image.open(cover_path).convert("RGB")
arr = np.array(img)                         # H x W x 3
secret = open(secret_path, "rb").read()
payload = b"IDST" + len(secret).to_bytes(4,"big") + zlib.crc32(secret).to_bytes(4,"big") + secret

H,W,C = arr.shape
cap_bits = H*W*C
need_bits = len(payload)*8
if need_bits > cap_bits:
    print(f"[-] Secret too large: {len(payload)} bytes > {cap_bits//8} bytes cap"); sys.exit(1)

flat = arr.reshape(-1)                      # interleaved R,G, B
bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
flat[:bits.size] = (flat[:bits.size] & 0xFE) | bits
out = flat.reshape(arr.shape)
Image.fromarray(out, "RGB").save(stego_path, optimize=True)
print(f"[+] Wrote {stego_path} with {len(payload)} bytes embedded")
