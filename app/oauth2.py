from jose import jwt, JWTError
from datetime import datetime, timedelta

# Secret key and algorithm configuration
SECRET_KEY = "28f70e119a4c13c80ea3e6e42cb9b79d197ef2f3ade84ad67ff4c041d6ddb4f4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create the access token
def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode the token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
