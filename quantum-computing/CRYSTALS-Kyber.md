# CRYSTALS-Kyber Post-Quantum Key Exchange

This project evaluates and demonstrates the integration of the NIST-selected CRYSTALS-Kyber key encapsulation mechanism into classical security workflows. The goal is to prototype post-quantum ready key exchanges that can be adapted for TLS or bespoke secure messaging systems.

## Objectives
- Understand Kyber key generation, encapsulation, and decapsulation flows.
- Stand up a development environment with the [Open Quantum Safe liboqs](https://github.com/open-quantum-safe/liboqs) SDK or the Kyber reference code.
- Integrate Kyber into a TLS handshake or standalone secure messaging exchange.
- Capture performance metrics to estimate production viability.

## Environment Setup
1. Install the liboqs dependencies:
   ```bash
   sudo apt update
   sudo apt install -y cmake ninja-build python3 python3-pip libssl-dev
   ```
2. Clone and build liboqs:
   ```bash
   git clone --recursive https://github.com/open-quantum-safe/liboqs.git
   cd liboqs
   mkdir build && cd build
   cmake -GNinja -DOQS_BUILD_ONLY_LIB=ON ..
   ninja
   sudo ninja install
   ```
3. (Optional) Build OpenSSL with OQS provider support to enable Kyber-based TLS:
   ```bash
   git clone --recursive https://github.com/open-quantum-safe/oqs-provider.git
   cd oqs-provider
   cmake -S . -B build -GNinja -DOQS_PROVIDER_BUILD_SHARED_LIBS=ON
   ninja -C build
   sudo ninja -C build install
   ```
4. For Python prototyping, install the `oqs` bindings:
   ```bash
   python3 -m pip install oqs
   ```

## Key Exchange Workflow
The example below demonstrates a hybrid workflow that uses Kyber-768 for key establishment inside a classical message exchange. The same primitives can be wired into a TLS handshake via the OQS OpenSSL provider.

```python
import oqs

kem_alg = "Kyber768"
with oqs.KeyEncapsulation(kem_alg) as server:
    server_public_key = server.generate_keypair()

    with oqs.KeyEncapsulation(kem_alg, server_public_key) as client:
        ciphertext, shared_secret_client = client.encap_secret()

    shared_secret_server = server.decap_secret(ciphertext)

assert shared_secret_client == shared_secret_server
print(f"Established {kem_alg} shared secret: {shared_secret_client.hex()}")
```

## TLS Handshake Integration
1. Build OpenSSL with the OQS provider and enable the desired Kyber variant (Kyber512/768/1024).
2. Generate provider-backed certificates:
   ```bash
   oqs-provider/test/oqs-ca.sh
   ```
3. Launch an OpenSSL server that negotiates a PQC KEM:
   ```bash
   ./apps/openssl s_server -provider oqsprovider -provider default -cert x509_pki/oqsserver_cert.pem -key x509_pki/oqsserver_key.pem -www
   ```
4. Connect with an OpenSSL client configured for PQC ciphersuites:
   ```bash
   ./apps/openssl s_client -provider oqsprovider -provider default -cert x509_pki/oqsclient_cert.pem -key x509_pki/oqsclient_key.pem -groups kyber768
   ```

## Testing & Performance Logging
- Use `oqs-test` or `tests/kat_kem` from liboqs to validate correctness.
- Capture CPU time and memory using `/usr/bin/time -v` while performing repeated encapsulation/decapsulation cycles.
- Compare handshake latency between classical and PQC-enabled TLS sessions.
- Document any incompatibilities encountered when integrating with legacy systems or middleware.

## Challenges & Considerations
- **Legacy compatibility:** Older TLS stacks may not accept PQC groups, requiring hybrid classical+PQC key shares.
- **Side-channel resilience:** Audit builds for constant-time behavior and consider masked implementations when deploying on shared hardware.
- **Certificate management:** Ensure tooling supports larger key sizes and algorithm identifiers introduced by PQC suites.

## Next Steps
- Benchmark and contrast Kyber performance against other NIST PQC finalists such as Dilithium and SABER.
- Build a Dockerized integration lab that automates liboqs/OpenSSL setup and runs regression tests.
- Prototype hybrid key exchanges that combine Kyber with classical ECDHE to ease migration risk.

## References
- [CRYSTALS-Kyber Specifications](https://pq-crystals.org/kyber/)
- [Open Quantum Safe Project](https://openquantumsafe.org/)
- [NIST Post-Quantum Cryptography Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
