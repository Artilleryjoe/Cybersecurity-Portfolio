from PIL import Image
import numpy as np, zlib, sys

stego_path = "stego.png"
img = Image.open(stego_path).convert("RGB")
arr = np.array(img)
bits = (arr.reshape(-1) & 1)

# header: 4 bytes magic + 4 length + 4 crc = 12 bytes
hdr = np.packbits(bits[:96]).tobytes()
if hdr[:4] != b"IDST":
    print("[-] No header found"); sys.exit(1)
length = int.from_bytes(hdr[4:8], "big")
crc_ref = int.from_bytes(hdr[8:12], "big")

need_bits = (12 + length) * 8
payload = np.packbits(bits[:need_bits]).tobytes()
secret = payload[12:12+length]
crc = zlib.crc32(secret)
open("recovered.txt", "wb").write(secret)
print(f"[+] Recovered {len(secret)} bytes to recovered.txt (CRC {'OK' if crc==crc_ref else 'BAD'})")
