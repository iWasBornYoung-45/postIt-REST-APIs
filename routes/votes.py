from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
import models
from utils import get_current_user
import schemas

router = APIRouter(prefix='/vote', tags=['Votes'])

@router.post('/')
async def upvote_or_downvote(payload: schemas.VoteSchema, db: Annotated[Session, Depends(get_db)], curr_user: Annotated[models.Users, Depends(get_current_user)]):
    if not db.query(models.Posts).filter(models.Posts.id == payload.post_id, models.Posts.published == True).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    query = db.query(models.Upvotes).filter(models.Upvotes.post_id == payload.post_id, models.Upvotes.user_id == curr_user.user_id)
    liked_post = query.first()
    if payload.vote:
        if liked_post:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='cannot upvote twice')
        vote = models.Upvotes(post_id = payload.post_id, user_id = curr_user.user_id)
        db.add(vote)
        db.commit()
        return {"message": "post upvoted!"}
    if not liked_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no liked post found')
    query.delete(synchronize_session=False)
    db.commit()
    return {"message": "post downvoted!"}
