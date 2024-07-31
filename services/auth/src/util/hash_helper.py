from __future__ import annotations

from functools import lru_cache

from argon2 import PasswordHasher


@lru_cache(maxsize=1)
def get_hasher():
    return PasswordHasher()
