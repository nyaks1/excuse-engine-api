from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
import os

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

# Database Setup 

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model 

class Excuse(Base):
    __tablename__ = "excuses"

    id       = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    text     = Column(String)

#  Create Tables 

Base.metadata.create_all(bind=engine)

# Pydantic Models

class ExcuseRequest(BaseModel):
    category: str = "work"
    urgency: int = 1
    name: Optional[str] = None

class ExcuseCreate(BaseModel):
    category: str
    text: str

# App

app = FastAPI(
    title="ExcuseEngine API",
    description="Because accountability is overrated.",
    version="2.0.0"
)

VALID_CATEGORIES = ["work", "gym", "code", "family"]

prefix = {
    1: "",
    2: "Look, honestly — ",
    3: "I swear — "
}

#  Dependency 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Seed Data 

def seed_database(db: Session):
    if db.query(Excuse).count() > 0:
        return

    excuses = [
        Excuse(category="work", text="My laptop updated right before the deadline."),
        Excuse(category="work", text="I was in a meeting about having too many meetings."),
        Excuse(category="work", text="The WiFi was slow and I didn't want to submit broken work."),
        Excuse(category="gym",  text="I was going to go, but I hydrated wrong."),
        Excuse(category="gym",  text="Rest days are part of the program. This is my 4th rest day."),
        Excuse(category="gym",  text="My gym shoes are still damp from last time."),
        Excuse(category="code", text="It works on my computer."),
        Excuse(category="code", text="I was refactoring. The bug is a feature now."),
        Excuse(category="code", text="The tests were passing before I touched it."),
        Excuse(category="family", text="I didn't see the message until just now."),
        Excuse(category="family", text="I was on my way but remembered I left the stove on."),
        Excuse(category="family", text="Signal was bad the whole day."),
    ]

    db.add_all(excuses)
    db.commit()

#  Routes 

@app.get("/")
def root():
    return {
        "message": "ExcuseEngine API is running",
        "version": "2.0.0",
        "endpoints": ["/excuse", "/excuses/add", "/categories", "/docs"]
    }

@app.get("/categories")
def list_categories():
    return {"categories": VALID_CATEGORIES}

@app.get("/excuse")
def get_excuse(
    category: str = Query(default="work", description="work | gym | code | family"),
    urgency: int = Query(default=1, ge=1, le=3, description="1=chill, 3=desperate"),
    db: Session = Depends(get_db)
):
    """Returns a random excuse from the database."""

    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available: {VALID_CATEGORIES}"
        )

    seed_database(db)

    excuses = db.query(Excuse).filter(Excuse.category == category).all()

    if not excuses:
        raise HTTPException(
            status_code=404,
            detail=f"No excuses found for category '{category}'"
        )

    excuse = random.choice(excuses)

    return {
        "category": category,
        "urgency": urgency,
        "excuse": f"{prefix[urgency]}{excuse.text}"
    }

@app.post("/excuse")
def post_excuse(request: ExcuseRequest, db: Session = Depends(get_db)):
    """Submit your situation, get your excuse."""

    if request.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{request.category}' not found. Available: {VALID_CATEGORIES}"
        )

    if request.urgency < 1 or request.urgency > 3:
        raise HTTPException(
            status_code=422,
            detail="Urgency must be between 1 and 3"
        )

    seed_database(db)

    excuses = db.query(Excuse).filter(Excuse.category == request.category).all()
    excuse = random.choice(excuses)
    greeting = f"{request.name}, " if request.name else ""

    return {
        "category": request.category,
        "urgency": request.urgency,
        "excuse": f"{greeting}{prefix[request.urgency]}{excuse.text}"
    }

@app.post("/excuses/add")
def add_excuse(payload: ExcuseCreate, db: Session = Depends(get_db)):
    """Add a new excuse to the database."""

    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{payload.category}' not found. Available: {VALID_CATEGORIES}"
        )

    new_excuse = Excuse(category=payload.category, text=payload.text)
    db.add(new_excuse)
    db.commit()
    db.refresh(new_excuse)

    return {
        "message": "Excuse added successfully",
        "id": new_excuse.id,
        "category": new_excuse.category,
        "text": new_excuse.text
    }