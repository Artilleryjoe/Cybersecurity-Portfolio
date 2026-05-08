# QRNG Steganography (LSB Demo)

This folder demonstrates simple least-significant-bit (LSB) steganography.

> **Carrier note:** in this repo, `qrng.png` is an **actual QRNG-derived image** (vacuum fluctuations from ANU's QRNG project), i.e., true random entropy.

## Files

- `embed.py` / `extract.py`: basic sequential LSB hide/recover.
- `embed_keyed.py` / `extract_keyed.py`: same logic, but bit positions are shuffled with a deterministic passphrase-derived seed:
  - `hashlib.sha256(passphrase.encode()).digest()`
- `generate_sample_cover.py`: optional synthetic 512x512 high-entropy cover generator for local testing when a real QRNG image is unavailable.
- `requirements.txt`: Python dependencies.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Inputs

- Expected cover image path: `qrng.png`
- Secret file path: `secret.txt`

If you already have the tracked real QRNG `qrng.png`, use it directly.
If needed for local experiments only, you can generate a synthetic replacement:

```bash
python generate_sample_cover.py
```

Create secret:

```bash
echo "Steganography test" > secret.txt
```

## Basic mode

Embed:

```bash
python embed.py
```

Extract:

```bash
python extract.py
```

Verify:

```bash
cmp -s secret.txt recovered.txt && echo "Match" || echo "Mismatch"
```

## Keyed mode

Embed (prompts for passphrase):

```bash
python embed_keyed.py
```

Extract (same passphrase required):

```bash
python extract_keyed.py
```

## Data format

Both modes write:

1. First 4 bytes = big-endian secret length.
2. Remaining bytes = secret payload.

Bits are stored in the LSB of RGB channels.
