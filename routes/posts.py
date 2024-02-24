import models, schemas, utils
from fastapi import status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from database import get_db
from uuid import UUID
from typing import Annotated
from sqlalchemy import func

router = APIRouter(prefix='/posts', tags=['Posts'])

@router.get('/', response_model = list[schemas.PostsResponseBody])
async def get_posts(db: Annotated[Session, Depends(get_db)], limit: Annotated[int | None, Query(le=10)] = 5, id: UUID | None  = None, skip: int | None = 0, search: str | None = ""):
    query = db.query(models.Posts, func.count(models.Upvotes.post_id).label("upvote_count")).join(models.Upvotes, models.Posts.id == models.Upvotes.post_id, isouter=True)
    if not id:
        query = query.filter(models.Posts.published == True, models.Posts.title.contains(search)).group_by(models.Posts.id).limit(limit).offset(skip)
    else:
        query = query.filter(models.Posts.published == True, models.Posts.id == id).group_by(models.Posts.id)
    res = query.all()
    res = sorted([{'post': post, 'upvotes': upvotes} for post, upvotes in res], key=lambda x:x['upvotes'], reverse=True)
    return res

@router.post('/', response_model=schemas.ResponseBody, status_code=status.HTTP_201_CREATED)
async def add_post(payload: schemas.BodySchema, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.Users, Depends(utils.get_current_user)]):
    print(current_user.user_id)
    post = models.Posts(op_id = current_user.user_id, **payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.put('/', response_model=schemas.ResponseBody, status_code=status.HTTP_200_OK)
async def update_post(id: UUID, payload: schemas.BodySchema, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.Users, Depends(utils.get_current_user)]):
    curr_post = db.query(models.Posts).filter(models.Posts.id == id).first()
    if not curr_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found")
    if curr_post.op_id == current_user.user_id:
        db.query(models.Posts).filter(models.Posts.id == id).update(values= payload.model_dump(), synchronize_session=False)
        db.commit()
        updated_post = db.query(models.Posts).filter(models.Posts. id == id).first()
        return updated_post
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: str, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.Users, Depends(utils.get_current_user)]):
    curr_post = db.query(models.Posts).filter(models.Posts.id == id).first()
    if not curr_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found")
    if current_user.user_id != curr_post.op_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    db.query(models.Posts).filter(models.Posts.id == id).delete(synchronize_session=False)
    db.commit()