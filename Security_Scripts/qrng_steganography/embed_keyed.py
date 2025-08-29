# keyed LSB embed: qrng.png + secret.txt -> stego.png (needs passphrase)
from PIL import Image
import numpy as np, zlib, sys, getpass, hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

cover, secret_path, out = "qrng.png", "secret.txt", "stego.png"
pwd = getpass.getpass("Passphrase: ").encode()

# derive a deterministic 32-byte key from passphrase + cover hash
cover_bytes = open(cover,"rb").read()
salt = hashlib.sha256(cover_bytes).digest()
hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"stego-path", backend=default_backend())
key = hkdf.derive(pwd)

img = Image.open(cover).convert("RGB")
arr = np.array(img)
H, W, C = arr.shape
N = H*W*C

secret = open(secret_path,"rb").read()
payload = b"IDKT" + len(secret).to_bytes(4,"big") + zlib.crc32(secret).to_bytes(4,"big") + secret

need_bits = len(payload)*8
if need_bits > N:
    print("[-] Too large: need", need_bits//8, "bytes, cap", N//8); sys.exit(1)

# build a permutation of channel indices using key
rng = np.random.default_rng(np.frombuffer(key, dtype=np.uint64))  # 32 bytes -> 4 uint64
perm = np.arange(N, dtype=np.int64)
rng.shuffle(perm)

# map payload bits onto shuffled positions
bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8)).astype(np.uint8)
flat = arr.reshape(-1)
sel = perm[:bits.size]
flat[sel] = (flat[sel] & 0xFE) | bits
Image.fromarray(flat.reshape(arr.shape), "RGB").save(out, optimize=True)
print(f"[+] wrote {out} (keyed path, {len(payload)} bytes embedded)")
