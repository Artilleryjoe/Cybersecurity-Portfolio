# QRNG-Based Steganography Experiment

Using a quantum random number generator (QRNG) image as the cover, this experiment hides text within pixel least-significant bits and verifies recovery and stealth.

## Objective
Evaluate whether high-entropy QRNG noise can conceal data without introducing visible or statistical artifacts.

## Methodology
- Generated a secret file and embedded it into a 256×256 QRNG PNG using `embed.py`.
- Extracted the payload with `extract.py` and validated integrity via CRC32.
- Enhanced security with a passphrase-derived pixel permutation in `embed_keyed.py` and `extract_keyed.py`.
- Compared cover and stego images visually and through chi-square analysis of LSB distribution.

## Results
- **Visual:** No discernible difference between `qrng.png` and `stego.png`.
- **Statistical:** LSB distribution remained ~50/50; chi-square remained low.
- **Security:** Keyed path prevents unauthorized extraction.

## Conclusions
QRNG images provide an excellent steganographic carrier. Their inherent randomness masks modifications, offering a covert channel for East Texas partners and research efforts in **Lindale** and **Tyler**.

## Files
- `embed.py`, `extract.py`
- `embed_keyed.py`, `extract_keyed.py`
- `qrng.png`, `stego.png`, `diff.png`, `secret.txt`

These resources support Iron Dillo's mission of veteran-owned cybersecurity for individuals, small businesses, and rural operations across East Texas.
