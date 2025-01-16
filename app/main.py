from fastapi import FastAPI, Response, status, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import logging

from .utils import hash

from . import models
from .database import engine
from .schemas import PostCreate ,Post ,UserCreate ,UserOut

models.Base.metadata.create_all(bind=engine)

from .database import get_db
from .routers import user , post



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()

# uvicorn app.main:app                                                                                                          



@app.get("/")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World!"}

from fastapi.encoders import jsonable_encoder

app.include_router(user.router)
app.include_router(post.router)


