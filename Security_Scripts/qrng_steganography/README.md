# QRNG Steganography

Low-level scripts demonstrating least-significant-bit (LSB) steganography using a quantum random number generator (QRNG) image as the cover. The high entropy of QRNG noise makes it an ideal carrier for hidden messages.

## Setup

### 1. Create and activate a virtual environment

**Bash**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**PowerShell**
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Place a QRNG image
Save your quantum-noise PNG in this directory as `qrng.png`.

Quick sanity check:
```bash
python - <<'PY'
from PIL import Image
im = Image.open('qrng.png')
print(im.mode, im.size)
PY
```

### 3. Create a secret to hide
```bash
echo "Steganography test — $(date)" > secret.txt
wc -c secret.txt
```
Keep the secret below the image capacity:
- Grayscale: `(width*height)/8` bytes
- RGB: `(width*height*3)/8` bytes

## Usage

### Embed
```bash
python embed.py
```
Produces `stego.png` with the secret embedded.

### Extract
```bash
python extract.py
```
Writes the recovered data to `recovered.txt`.

### Keyed Embed/Extract
```bash
python embed_keyed.py    # prompts for passphrase
python extract_keyed.py  # use same passphrase
```
A passphrase-derived permutation randomizes which pixels carry data.

### Verify Secret Recovery
**Linux/macOS**
```bash
cmp -s secret.txt recovered.txt && echo "Match ✅" || echo "Mismatch ❌"
```

**Windows PowerShell**
```powershell
if (Compare-Object (Get-Content secret.txt) (Get-Content recovered.txt)) { "Mismatch ❌" } else { "Match ✅" }
```

### Optional Diff Visualization
```bash
python - <<'PY'
from PIL import Image, ImageChops
a = Image.open('qrng.png').convert('RGB')
b = Image.open('stego.png').convert('RGB')
ImageChops.difference(a,b).save('diff.png')
print('Wrote diff.png')
PY
```
`diff.png` should appear as uniform speckle; visible patterns indicate an issue.

## Sample Assets
Sample `qrng.png`, `stego.png`, `diff.png`, and `secret.txt` are included. PNG files are tracked with Git LFS to keep the repository lightweight.
