"""哈希加密模块 - 使用 SHA-256 + 随机盐值对密码进行加密存储"""
import hashlib
import os
import secrets


def generate_salt(length: int = 16) -> str:
    """生成随机盐值"""
    return secrets.token_hex(length)


def hash_password(password: str, salt: str = None) -> dict:
    """
    对密码进行 SHA-256 加盐哈希
    返回 {"salt": ..., "hash": ...}
    """
    if salt is None:
        salt = generate_salt()
    # 多轮迭代增强安全性
    iterations = 10000
    digest = password.encode("utf-8") + salt.encode("utf-8")
    for _ in range(iterations):
        digest = hashlib.sha256(digest).digest()
    return {"salt": salt, "hash": digest.hex()}


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """校验密码是否匹配"""
    result = hash_password(password, salt)
    return result["hash"] == stored_hash


def hash_token(text: str) -> str:
    """对普通文本生成单一哈希（用于 session token 等）"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
