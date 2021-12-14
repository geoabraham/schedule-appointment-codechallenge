import hashlib
import random
import string

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_bcrypt(pwd: str):
    return pwd_context.hash(pwd)


def verify_bcrypt_hash(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def hash_md5(pwd: str) -> str:
    return hashlib.md5(str.encode(pwd)).hexdigest()


def salt_generator() -> str:
    salt = ""
    for _ in range(0, 64):
        salt += random.choice(string.ascii_letters + string.digits)
    return str(salt)
