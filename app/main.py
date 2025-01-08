from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg
import psycopg.rows
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432)),  # Default to 5432 if DB_PORT is not set
}

# Dependency for database connection
def get_db_connection():
    try:
        conn = psycopg.connect(**DB_CONFIG, row_factory=psycopg.rows.dict_row)
        yield conn
    finally:
        conn.close()

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

@app.get("/posts", response_model=List[dict])
def get_posts(db: psycopg.Connection = Depends(get_db_connection)):
    logger.info("Fetching all posts from the database.")
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM posts;")
            posts = cur.fetchall()
            if not posts:
                logger.warning("No posts found.")
                return {"data": [], "message": "No posts available."}
            logger.info(f"Fetched {len(posts)} posts.")
            return posts
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching posts."
        )

@app.get("/posts/{post_id}")
def get_post(post_id: int, db: psycopg.Connection = Depends(get_db_connection)):
    logger.info(f"Fetching post with ID: {post_id}")
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM posts WHERE id = %s;", (post_id,))
            post = cur.fetchone()
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
def create_post(post: Post, db: psycopg.Connection = Depends(get_db_connection)):
    logger.info(f"Creating a new post with title: {post.title}")
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING id;",
                (post.title, post.content, post.published)
            )
            post_id = cur.fetchone()["id"]
            db.commit()
            logger.info(f"Post created with ID: {post_id}")
            return {"id": post_id, **post.model_dump()}
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the post."
        )

@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db: psycopg.Connection = Depends(get_db_connection)):
    logger.info(f"Updating post with ID: {post_id}")
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING id;",
                (post.title, post.content, post.published, post_id)
            )
            updated_post = cur.fetchone()
            if not updated_post:
                logger.warning(f"Post with ID {post_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with ID {post_id} not found."
                )
            db.commit()
            logger.info(f"Post with ID {post_id} updated successfully.")
            return {"id": post_id, **post.dict()}
    except Exception as e:
        logger.error(f"Error updating post with ID {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the post."
        )

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: psycopg.Connection = Depends(get_db_connection)):
    logger.info(f"Deleting post with ID: {post_id}")
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE id = %s RETURNING id;", (post_id,))
            deleted_post = cur.fetchone()
            if not deleted_post:
                logger.warning(f"Post with ID {post_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with ID {post_id} not found."
                )
            db.commit()
            logger.info(f"Post with ID {post_id} deleted successfully.")
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting post with ID {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the post."
        )
