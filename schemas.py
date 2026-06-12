from pydantic import BaseModel

class BlogCreate(BaseModel):
    title:str
    content:str

class BlogResponse(BaseModel):
    id:int
    title:str
    content:str
    model_config = {"from_attributes": True}
        
