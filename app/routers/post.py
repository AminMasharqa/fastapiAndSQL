from .. import models ,schemas,utils

from fastapi import FastAPI, Response, status, HTTPException, Depends ,APIRouter
from typing import List
from sqlalchemy.orm import Session
import logging
from ..database import get_db

from ..schemas import Post  ,PostCreate

from ..oauth2 import get_current_user
from .. import oauth2


router = APIRouter(
    prefix="/posts"
)
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__) 

@router.get("/",response_model=List[Post])  # Use the Post Pydantic model
def get_posts(db: Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
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

        


@router.get("/{post_id}",response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
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

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    logger.info(f"Creating a new post with title: {post.title}")
    try:
        # print(current_user)
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

@router.put("/{post_id}",response_model=Post)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
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

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),current_user : int = Depends(oauth2.get_current_user)):
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
