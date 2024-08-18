import string
import secrets


def create_random_key(length: int = 4) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
