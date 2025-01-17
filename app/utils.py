from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str) -> bool:
    """Verify that the plaintext password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)
