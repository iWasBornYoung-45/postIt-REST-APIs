import models, utils, schemas
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from typing import Annotated
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(prefix='/users', tags=['Users'])

@router.post('/', response_model=schemas.UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_user(payload: schemas.UserBodySchema, db: Session = Depends(get_db)):
    payload.password = utils.hash_str(payload.password)
    user = models.Users(**payload.model_dump())
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"email:'{payload.email}' and/or phone number: '{payload.phone}' already exists")
    return user

@router.put('/', status_code=status.HTTP_200_OK)
async def change_password(payload: schemas.PasswordChangeBody, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.Users, Depends(utils.get_current_user)]):
    if not (payload.email or payload.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="neither phone number nor email provided")
    rowcount = db.query(models.Users).filter((models.Users.phone == payload.phone) | (models.Users.email == payload.email)).update({models.Users.password: utils.hash_str(payload.password)})
    db.commit()
    if not rowcount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="credentials not found")
    return {"message": "password updated"}

@router.get('/', response_model=schemas.UserResponseSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user id: {user_id} not found")
    return user

@router.post('/auth', status_code=status.HTTP_202_ACCEPTED)
def user_auth(form_payload: Annotated[OAuth2PasswordRequestForm, Depends(schemas.login_cred)], db: Annotated[Session, Depends(get_db)]):
    if isinstance(form_payload.username, str):
        user = db.query(models.Users).filter(models.Users.email == form_payload.username).first()
    else:
        user = db.query(models.Users).filter(models.Users.phone == form_payload.username).first()  
    if not (user and utils.check_pass(form_payload.password, user.password)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="email or phone number not found/ incorrect password")
    access_token = utils.create_access_token(data = {"user_id": user.user_id})
    return {"access_token": access_token, "token_type": "Bearer"}

@router.get('/my-posts', response_model = list[schemas.ResponseBody])
def get_user_posts(db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.Users, Depends(utils.get_current_user)]):
    user_posts = db.query(models.Posts).filter(models.Posts.op_id == current_user.user_id).all()
    return user_posts
    
