
from fastapi import FastAPI, Response, status, HTTPException, Depends ,APIRouter
from typing import List
from sqlalchemy.orm import Session
import logging
from .. import models ,schemas,utils
from ..schemas import UserCreate,UserOut
from ..database import get_db
import logging


router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@router.post("/users",status_code=status.HTTP_201_CREATED,response_model=UserOut)
def create_user(user:UserCreate,db: Session = Depends(get_db)):
    logger.info(f"Creating a new User with email: {user.email}")
    try:
        #hash the password  - user.password
        hashed_password = hash(user.password)
        user.password= hashed_password 
        new_user = models.User(**user.model_dump())
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

    
    
@router.get('/users/{id}',response_model=UserOut)
def get_user(id: int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with id : {id} does not exist")
    
    return user
    