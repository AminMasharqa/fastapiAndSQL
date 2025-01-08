from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging

from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

from .database import get_db



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Hello World!"}

from fastapi.encoders import jsonable_encoder

@app.get("/posts")  # Use the Post Pydantic model
def get_posts(db: Session = Depends(get_db)):
    logger.info("Fetching all posts from the database.")
    try:
        posts = db.query(models.Post).all()
        if not posts:
            logger.warning("No posts found.")
            return []
        logger.info(f"Fetched {len(posts)} posts.")
        return posts  # Convert ORM objects to JSON serializable format
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching posts."
        )
        
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return  {"details:":posts}
        


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching post with ID: {post_id}")
    try:
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            logger.warning(f"Post with ID {post_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found."
            )
        logger.info(f"Post with ID {post_id} fetched successfully.")
        return post
    except Exception as e:
        logger.error(f"Error fetching post with ID {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the post."
        )

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    logger.info(f"Creating a new post with title: {post.title}")
    try:
        new_post = models.Post(**post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        logger.info(f"Post created with ID: {new_post.id}")
        return new_post
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the post."
        )

@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: Session = Depends(get_db)):
    logger.info(f"Updating post with ID: {post_id}")
    try:
        existing_post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not existing_post:
            logger.warning(f"Post with ID {post_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found."
            )
        for key, value in post.model_dump().items():
            setattr(existing_post, key, value)
        db.commit()
        db.refresh(existing_post)
        logger.info(f"Post with ID {post_id} updated successfully.")
        return existing_post
    except Exception as e:
        logger.error(f"Error updating post with ID {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the post."
        )

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting post with ID: {post_id}")
    try:
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            logger.warning(f"Post with ID {post_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found."
            )
        db.delete(post)
        db.commit()
        logger.info(f"Post with ID {post_id} deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting post with ID {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the post."
        )


