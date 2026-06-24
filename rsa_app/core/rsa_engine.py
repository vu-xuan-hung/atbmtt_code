
import random
import math
import hashlib
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class RSAPublicKey:
    e: int  
    n: int  

    def __str__(self):
        return f"e = {self.e}\nn = {self.n}"


@dataclass
class RSAPrivateKey:
    d: int  
    n: int  

    def __str__(self):
        return f"d = {self.d}\nn = {self.n}"


@dataclass
class RSAKeyPair:
    public_key: RSAPublicKey
    private_key: RSAPrivateKey
    p: int
    q: int
    phi_n: int


def gcd(a: int, b: int) -> int:
    """Tính ước chung lớn nhất (GCD) bằng thuật toán Euclid."""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Thuật toán Euclid mở rộng.
    Trả về (g, x, y) sao cho a*x + b*y = g = gcd(a, b).
    """
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def mod_inverse(e: int, phi: int) -> Optional[int]:
    """
    Tính nghịch đảo modular của e theo phi.
    Trả về d sao cho (e * d) % phi == 1, hoặc None nếu không tồn tại.
    """
    g, x, _ = extended_gcd(e % phi, phi)
    if g != 1:
        return None
    return x % phi


def power_mod(base: int, exp: int, mod: int) -> int:
    """Tính (base^exp) % mod bằng thuật toán bình phương nhanh (fast exponentiation)."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result


# ---------------------------------------------------------------------------
#                   Miller-Rabin
# ---------------------------------------------------------------------------

def _miller_rabin_test(n: int, a: int) -> bool:
    """Thực hiện một vòng kiểm tra Miller-Rabin với nhân chứng a."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Viết n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    x = power_mod(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(r - 1):
        x = power_mod(x, 2, n)
        if x == n - 1:
            return True
    return False


def is_prime(n: int, k: int = 20) -> bool:
    """
    Kiểm tra số nguyên tố bằng thuật toán Miller-Rabin xác suất.
    k: số vòng kiểm tra (càng cao càng chính xác).
    """
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not _miller_rabin_test(n, a):
            return False
    return True


def generate_prime(bits: int) -> int:
    """Sinh một số nguyên tố ngẫu nhiên có độ dài `bits` bit."""
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) 
        candidate |= 1                 
        if is_prime(candidate):
            return candidate


# ---------------------------------------------------------------------------
#                           Sinh khóa RSA
# ---------------------------------------------------------------------------

def generate_rsa_keys(bits: int = 512) -> RSAKeyPair:
    """
    Sinh cặp khóa RSA.

    Tham số:
        bits: Độ dài bit của mỗi số nguyên tố p, q (mặc định 512).
              Modulus n sẽ có độ dài khoảng 2*bits.

    Trả về RSAKeyPair chứa đầy đủ thông tin.
    """
    while True:
        p = generate_prime(bits)
        q = generate_prime(bits)
        if p != q:
            break

    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537  
    if gcd(e, phi_n) != 1:
        e = 3
        while gcd(e, phi_n) != 1:
            e += 2
    d = mod_inverse(e, phi_n)

    public_key = RSAPublicKey(e=e, n=n)
    private_key = RSAPrivateKey(d=d, n=n)

    return RSAKeyPair(
        public_key=public_key,
        private_key=private_key,
        p=p,
        q=q,
        phi_n=phi_n,
    )


# ---------------------------------------------------------------------------
#                          Hash thông điệp
# ---------------------------------------------------------------------------

HASH_ALGORITHMS = {
    "MD5":    hashlib.md5,
    
}


def hash_message(message: str, algorithm: str = "MD5") -> Tuple[str, int]:
    """
    Hash thông điệp bằng thuật toán chỉ định.

    Trả về:
        (hex_digest: str, int_digest: int)
    """
    algo_fn = HASH_ALGORITHMS.get(algorithm)
    if algo_fn is None:
        raise ValueError(f"Thuật toán không hỗ trợ: {algorithm}")
    digest = algo_fn(message.encode("utf-8")).hexdigest()
    return digest, int(digest, 16)


# ---------------------------------------------------------------------------
#                              Ký số và Xác minh
# ---------------------------------------------------------------------------

def sign_message(message: str, private_key: RSAPrivateKey, algorithm: str = "MD5") -> Tuple[str, str, int]:
    """
    Tạo chữ ký số cho thông điệp.

    Bước:
        1. Hash thông điệp -> H(m)
        2. Mã hóa hash bằng private key: S = H(m)^d mod n

    Trả về:
        (hash_hex: str, signature_hex: str, signature_int: int)
    """
    hash_hex, hash_int = hash_message(message, algorithm)

    # Đảm bảo hash_int < n đưa giá trị băm về phạm vi các số mà RSA làm việc
    hash_int = hash_int % private_key.n

    # S = hash^d mod n
    signature_int = power_mod(hash_int, private_key.d, private_key.n)
    signature_hex = hex(signature_int)[2:] 

    return hash_hex, signature_hex, signature_int


def verify_signature(
    message: str,
    signature_hex: str,
    public_key: RSAPublicKey,
    algorithm: str = "MD5"
) -> Tuple[bool, str, str]:
    """
    Xác minh chữ ký số.

    Bước:
        1. Giải mã chữ ký bằng public key: H' = S^e mod n
        2. Hash thông điệp: H = Hash(m)
        3. So sánh H' và H

    Trả về:
        (is_valid: bool, original_hash_hex: str, decrypted_hash_hex: str)
    """
    try:
        signature_int = int(signature_hex, 16)
    except ValueError:
        return False, "", ""

    # Giải mã chữ ký: H' = S^e mod n
    decrypted_int = power_mod(signature_int, public_key.e, public_key.n)
    decrypted_hex = hex(decrypted_int)[2:]

    # Hash thông điệp gốc
    original_hex, original_int = hash_message(message, algorithm)
    original_int = original_int % public_key.n
    original_hex_mod = hex(original_int)[2:]

    is_valid = (decrypted_hex == original_hex_mod)
    return is_valid, original_hex, decrypted_hex
