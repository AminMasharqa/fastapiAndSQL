
from fastapi import FastAPI, Response, status, HTTPException, Depends ,APIRouter
from typing import List
from sqlalchemy.orm import Session
import logging
from .. import models ,schemas,utils
from ..schemas import UserCreate,UserOut
from ..database import get_db
import logging


router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating a new user with email: {user.email}")
    try:
        # Hash the password
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        
        # Create a new user instance
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User created with ID: {new_user.id}")
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user."
        )

    
@router.get('/{id}',response_model=UserOut)
def get_user(id: int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with id : {id} does not exist")
    
    return user
    
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting post with ID: {user_id}")
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Post with ID {user_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {user_id} not found."
            )
        db.delete(user)
        db.commit()
        logger.info(f"User with ID {user_id} deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user."
        )
