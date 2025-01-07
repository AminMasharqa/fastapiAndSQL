from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    

my_posts=[{"title":"Post 1", "content":"Content 1", "published":True, "rating":5,"id":1},
          {"title":"favouite foods"     , "content":"I like pizza","id":2}]


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post
    return None 


@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/posts/latest")
def get_latest_post():
    return {"latest_post": my_posts[-1]} if my_posts else {"message":"No posts found"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}



@app.get("/posts/{post_id}")
def get_post(post_id: int):
    print(type(post_id))
    post=find_post(post_id)
    print(post)
    return {"post_details:" : post} if post else {"message":"Post not found"} 


@app.post("/posts")
def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(1000000000)
    
    my_posts.append(post_dict)
    return {"data": post_dict}
