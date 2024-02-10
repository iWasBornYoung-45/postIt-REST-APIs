import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import main
from fastapi import HTTPException, status
from typing import Annotated
from database import get_db
from sqlalchemy.orm import Session
import models

main.load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'users/auth')

ALGO = "HS256"
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ACCESS_TOKEN_EXPIRY_MIN = 15

def hash_str(string: str) -> str:
    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()

def check_pass(payload_pass: str, hashed_pass: str) -> bool:
    return bcrypt.checkpw(payload_pass.encode(), hashed_pass.encode())

def create_access_token(data: dict):
    expire_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MIN)
    to_encode = data.copy()
    to_encode.update({"expire_at": str(expire_at)})
    access_token = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGO)
    return access_token

def verify_access_token(access_token: str):
    try:
        jwt_payload = jwt.decode(access_token, key=SECRET_KEY, algorithms=[ALGO])
        user_id = jwt_payload.get('user_id')
        if not user_id:
            return False
        return user_id
    except JWTError:
        return False
    
def get_current_user(access_token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    curr_user_id = verify_access_token(access_token)
    if not curr_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials", headers={"WWW-Authentication": "Bearer"})
    current_user = db.query(models.Users).filter(models.Users.user_id == curr_user_id).first()
    return current_user
