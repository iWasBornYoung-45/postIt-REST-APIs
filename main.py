from fastapi import FastAPI
from dotenv import main
import models
from database import engine
from routes import posts, users, votes
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="postIt!", description="REST services for postIt!")
main.load_dotenv()

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(votes.router)

@app.get('/', tags = ['Root'])
async def root():
    return {'msg': 'Hello World!'}






    

