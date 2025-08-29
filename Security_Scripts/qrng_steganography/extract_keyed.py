from PIL import Image
import numpy as np, zlib, sys, getpass, hashlib
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

stego = "stego.png"
pwd = getpass.getpass("Passphrase: ").encode()

img = Image.open(stego).convert("RGB")
arr = np.array(img)
H, W, C = arr.shape
N = H*W*C

# same salt derivation from the image bytes (works if cover hash unchanged by lossless save)
salt = hashlib.sha256(open(stego,"rb").read()).digest()
hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"stego-path", backend=default_backend())
key = hkdf.derive(pwd)

rng = np.random.default_rng(np.frombuffer(key, dtype=np.uint64))
perm = np.arange(N, dtype=np.int64); rng.shuffle(perm)
flat = arr.reshape(-1)

def read_bytes(nbytes):
    idx = read_bytes.idx
    need = nbytes*8
    pos = perm[idx:idx+need]
    read_bytes.idx += need
    bits = (flat[pos] & 1).astype(np.uint8)
    return np.packbits(bits).tobytes()
read_bytes.idx = 0

hdr = read_bytes(12)
if hdr[:4] != b"IDKT":
    sys.exit("[-] wrong key or no payload")
length = int.from_bytes(hdr[4:8],"big")
crc_ref = int.from_bytes(hdr[8:12],"big")
secret = read_bytes(length)
crc = zlib.crc32(secret)
ok = "OK" if crc==crc_ref else "BAD"
open("recovered.txt","wb").write(secret)
print(f"[+] recovered {len(secret)} bytes (CRC {ok}) -> recovered.txt")
