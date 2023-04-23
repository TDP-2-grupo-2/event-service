import os
from jose import jwt
from datetime import datetime, timedelta
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 5


def create_access_token(user_id: int, rol: str) -> str:

    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"id": user_id, "rol": rol, "exp": expires_delta}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    print(token)
    decoded_jwt = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_jwt
