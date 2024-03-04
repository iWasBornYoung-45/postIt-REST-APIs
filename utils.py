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

ALGO = os.getenv('JWT_ALGORITHM')
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ACCESS_TOKEN_EXPIRY_MIN = int(os.getenv('ACCESS_TOKEN_EXPIRY_MIN'))

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
        if not jwt_payload.get('user_id'):
            return False
        return jwt_payload
    except JWTError:
        return False
    
def get_current_user(access_token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    jwt_payload = verify_access_token(access_token)
    curr_user_id = jwt_payload.get('user_id')
    if not curr_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate credentials", headers={"WWW-Authentication": "Bearer"})
    jwt_expiry_time = datetime.strptime(jwt_payload.get('expire_at'), "%Y-%m-%d %H:%M:%S.%f")
    if datetime.utcnow() > jwt_expiry_time:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="access token expired", headers={"WWW-Authentication": "Bearer"})
    current_user = db.query(models.Users).filter(models.Users.user_id == curr_user_id).first()
    return current_user
