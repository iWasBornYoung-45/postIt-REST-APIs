from fastapi import FastAPI
from dotenv import main
import models
from database import engine
from routes import posts, users, votes
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)
origins = ["*"]

app = FastAPI(title="postIt!", description="REST services for postIt!")
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

main.load_dotenv()

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(votes.router)

@app.get('/', tags = ['Root'])
async def root():
    return {'msg': 'Hello World!'}






    

