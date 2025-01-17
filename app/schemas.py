
from pydantic import BaseModel,EmailStr
from typing import Optional, List


from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True
    
    
    
class PostCreate(PostBase):
    pass



class Post(PostBase):
    id:int
    created_at:datetime
    
    


class UserCreate(BaseModel):
    email:EmailStr
    password:str
    

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_model=True

class userLogin(BaseModel):
    email:EmailStr
    password:str
    
    