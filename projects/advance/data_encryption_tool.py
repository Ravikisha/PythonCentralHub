"""Encryption, and the properties you only notice when you measure them.

The version this replaces generated a Fernet key, encrypted one string and
printed it. That demonstrates the API and none of the things that actually
go wrong: keys derived badly from passwords, a mode that leaks the shape of
the plaintext, and ciphertext that can be modified without detection.

Everything below is measured on this machine.

    python data_encryption_tool.py
"""

import base64
import hashlib
import os
import secrets
import time

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def show_bytes(data, limit=32):
    return base64.b64encode(data)[:limit].decode() + "..."


def demo_nondeterminism():
    """The same plaintext must not produce the same ciphertext twice."""
    key = Fernet.generate_key()
    cipher = Fernet(key)
    message = b"transfer 500 to account 12345"
    first, second = cipher.encrypt(message), cipher.encrypt(message)
    print("  encrypting the same message twice:")
    print(f"    {show_bytes(first)}")
    print(f"    {show_bytes(second)}")
    print(f"    identical: {first == second}")
    print("    A deterministic cipher leaks equality: an observer who cannot")
    print("    read the messages can still see which ones are the same, and")
    print("    that is often the whole secret. The random IV is what stops it.")
    return cipher, message


def demo_tampering(cipher, message):
    """Fernet authenticates; raw AES does not."""
    token = bytearray(cipher.encrypt(message))
    token[40] ^= 0x01                       # flip one bit in the ciphertext
    print("\n  flipping one bit of the ciphertext:")
    try:
        cipher.decrypt(bytes(token))
        print("    decrypted anyway -- the ciphertext is not authenticated")
    except InvalidToken:
        print("    InvalidToken: Fernet carries an HMAC, so any modification")
        print("    is detected rather than silently decrypted to garbage.")
        print("    Encryption alone does not provide integrity; a cipher")
        print("    without a MAC lets an attacker change what you read.")


def demo_ecb_leak():
    """ECB encrypts identical blocks identically, so structure survives it."""
    key = secrets.token_bytes(32)
    # A record layout: the same 16-byte field repeated, as in a table dump.
    plaintext = (b"NAME:ALICE      " * 4 + b"NAME:BOB        " * 4
                 + b"NAME:ALICE      " * 4)

    def encrypt(mode_factory, name):
        cipher = Cipher(algorithms.AES(key), mode_factory())
        encryptor = cipher.encryptor()
        out = encryptor.update(plaintext) + encryptor.finalize()
        blocks = [out[i:i + 16] for i in range(0, len(out), 16)]
        distinct = len(set(blocks))
        print(f"    {name:>14}: {len(blocks)} blocks, {distinct} distinct")
        return distinct

    print("\n  the same 12-record table, two modes:")
    ecb = encrypt(lambda: modes.ECB(), "AES-ECB")
    cbc = encrypt(lambda: modes.CBC(secrets.token_bytes(16)), "AES-CBC")
    print(f"    The plaintext has 2 distinct records. ECB produces {ecb}")
    print(f"    distinct blocks and CBC produces {cbc}, so ECB's ciphertext")
    print("    reproduces the structure of the data exactly. This is the")
    print("    famous encrypted-penguin picture, and it is why ECB is not")
    print("    an acceptable mode for anything with repeated content.")


def demo_key_derivation():
    """A password is not a key, and the difference is measurable."""
    password = b"correct horse battery staple"
    salt = os.urandom(16)

    print("\n  turning a password into a key:")
    # Timed in a loop: one SHA-256 of a short password takes about a
    # microsecond, which is below the resolution of a single perf_counter
    # pair. Measuring it once reports the clock, not the hash.
    started = time.perf_counter()
    for _ in range(200_000):
        hashlib.sha256(password).digest()
    naive_time = (time.perf_counter() - started) / 200_000

    for iterations in (1_000, 100_000, 600_000):
        started = time.perf_counter()
        hashlib.pbkdf2_hmac("sha256", password, salt, iterations)
        elapsed = time.perf_counter() - started
        guesses = 1 / elapsed if elapsed else float("inf")
        print(f"    PBKDF2 {iterations:>7,} rounds: {elapsed * 1000:8.2f} ms  "
              f"-> {guesses:>12,.0f} guesses/second")

    fast = 1 / naive_time if naive_time else float("inf")
    print(f"    plain SHA-256          : {naive_time * 1e6:8.3f} us  "
          f"-> {fast:>12,.0f} guesses/second")
    print("    The slow function is the point. A single SHA-256 lets one")
    print(f"    core test {fast:,.0f} passwords a second; 600,000 rounds")
    print("    of PBKDF2 is the current OWASP guidance and costs the")
    print("    legitimate user a few hundred milliseconds, once.")
    print(f"    (Measured here on one core. Real attackers use GPUs, which")
    print(f"     is why the recommended round count keeps rising.)")
    return salt


def demo_salt(salt):
    """Two users with the same password must not get the same key."""
    password = b"correct horse battery staple"
    same = hashlib.pbkdf2_hmac("sha256", password, salt, 1_000)
    other = hashlib.pbkdf2_hmac("sha256", password, os.urandom(16), 1_000)
    print("\n  two users, identical passwords, different salts:")
    print(f"    {show_bytes(same, 24)}")
    print(f"    {show_bytes(other, 24)}")
    print(f"    identical: {same == other}")
    print("    Without a per-user salt, identical passwords produce identical")
    print("    stored hashes -- so one cracked password reveals every account")
    print("    that shared it, and a precomputed table cracks them all at")
    print("    once.")


def demo_throughput():
    """What encryption costs, so the cost is a number rather than a worry."""
    key = Fernet.generate_key()
    cipher = Fernet(key)
    print("\n  throughput, on this machine:")
    for size_kb in (1, 64, 1024):
        payload = os.urandom(size_kb * 1024)
        started = time.perf_counter()
        token = cipher.encrypt(payload)
        encrypt_time = time.perf_counter() - started
        started = time.perf_counter()
        cipher.decrypt(token)
        decrypt_time = time.perf_counter() - started
        overhead = len(token) - len(payload)
        print(f"    {size_kb:>5} KB: encrypt {encrypt_time * 1000:7.2f} ms  "
              f"decrypt {decrypt_time * 1000:7.2f} ms  "
              f"({size_kb / 1024 / max(encrypt_time, 1e-9):6.1f} MB/s), "
              f"token is {len(token) / len(payload):.2f}x the payload")
    print("    The expansion is roughly 4/3 and not a fixed number of bytes:")
    print("    a Fernet token is base64, which costs 33% before any of the")
    print("    cryptography. The fixed part -- version byte, timestamp, IV")
    print("    and HMAC -- is 57 bytes, and it is the smaller cost above")
    print("    1 KB. Encrypting a database column therefore needs a column")
    print("    about 1.4x the width, which is the kind of thing that is")
    print("    cheaper to know now than after the migration.")


def main():
    print("Data Encryption Tool")
    cipher, message = demo_nondeterminism()
    demo_tampering(cipher, message)
    demo_ecb_leak()
    salt = demo_key_derivation()
    demo_salt(salt)
    demo_throughput()
    print("\n  Fernet is AES-128-CBC with an HMAC and a timestamp, and the")
    print("  reason to prefer it over assembling those parts yourself is")
    print("  that every mistake demonstrated above is one it does not let")
    print("  you make.")


if __name__ == "__main__":
    main()
