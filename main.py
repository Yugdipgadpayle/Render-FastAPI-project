from pathlib import Path
import sys

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from auth import create_token, verify_token

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from database import Base, engine, SessionLocal
import model as models
import schemas


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login():
    return{
        "access_token":create_token({"user":"admin"}),
        "token_type":"bearer  "
    }

@app.get("/")
def home():
    return {
        "message": "Blog API Started"
    }

# Create Blog
@app.post("/blogs", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db),user=Depends(verify_token)):
    new_blog = models.Blog(
        title=blog.title,
        content=blog.content
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# Read all Blog

@app.get("/blogs")
def get_blogd(page:int=1,
              limit:int=5,
              search:str=Query(default=""),
              db:Session=Depends(get_db)):

   query = db.query(models.Blog)
   if search:
       query = query.filter(models.Blog.title.ilike(f"%{search}%"))

   total = query.count()
   start = (page - 1) * limit
   blogs = query.offset(start).limit(limit).all()

   return {
       "page": page,
       "limit": limit,
       "total": total,
       "data": blogs
   }


# Read One Blog
@app.get("/blogs/{id}", response_model=schemas.BlogResponse)
def get_blog(id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog

# Update Blog API

@app.put("/blogs/{id}", response_model=schemas.BlogResponse)
def update_blog(id: int, blog: schemas.BlogCreate, db: Session = Depends(get_db)):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    existing_blog.title = blog.title
    existing_blog.content = blog.content

    db.commit()
    db.refresh(existing_blog)

    return existing_blog

# Delete Blog API
@app.delete("/blogs/{id}")
def delete_blog(id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()

    return {
        "message": "Blog deleted successfully"
    }

    