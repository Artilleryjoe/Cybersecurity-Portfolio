#!/usr/bin/env python3

import argparse

import numpy as np
from PIL import Image
import zlib

MAGIC = b"IDST"


def extract(stego_path: str, output: str) -> None:
    img = Image.open(stego_path).convert("RGB")
    arr = np.array(img)
    bits = (arr.reshape(-1) & 1)
    header = np.packbits(bits[:96]).tobytes()
    if header[:4] != MAGIC:
        raise SystemExit("[-] No payload header located")
    length = int.from_bytes(header[4:8], "big")
    crc_ref = int.from_bytes(header[8:12], "big")
    total_bits = (12 + length) * 8
    payload = np.packbits(bits[:total_bits]).tobytes()
    secret = payload[12:12 + length]
    crc = zlib.crc32(secret)
    with open(output, "wb") as fh:
        fh.write(secret)
    status = "OK" if crc == crc_ref else "BAD"
    print(f"[+] Recovered {len(secret)} bytes to {output} (CRC {status})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract LSB-hidden payloads")
    parser.add_argument("--stego", default="stego.png", help="Image containing hidden data")
    parser.add_argument("--output", default="recovered.txt", help="File to write the extracted secret")
    args = parser.parse_args()
    extract(args.stego, args.output)


if __name__ == "__main__":
    main()
