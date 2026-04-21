from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import random

class ExcuseRequest (BaseModel) :
       category: str = "work"
       urgency: int = 1
       name: Optional[str] = None

app = FastAPI(
    title ="ExcuseEngine API",
    description="Because accountability is overrated.",
    version="1.0.0"
)

EXCUSES = {
    "work": [
            "My laptop updated right before the deadline.",
            "I was in a meeting about having too many meetings.",
            "The WiFi was slow and I didn't want to submit broken work.",
    ],
    "gym": [
            "I was going to go, but I hydrated wrong.",
            "Rest days are part of the program. This is my 4th rest day.",
            "My gym shoes are still damp from last time.",
    ],
    "code": [
            "It works on my machine.",
            "I was refactoring. The bug is a feature now.",
            "The tests were passing before I touched it.",
    ],
    "family": [
            "I didn't see the message until just now.",
            "I was on my way but remembered I left the stove on.",
            "Signal was bad the whole day.",
    ]
}

prefix = {
                1: "",
                2: "Look, honestly —  ",
                3: "I swear —"
        }

@app.get("/excuse")
def get_excuse (
    category: str =Query(default="work", description= "work | gym | code | family"),
    urgency: int = Query(default=1, ge=1, le=3, description="1=chill, 3=desperate")
    ):
        """Returns a random excuse. No questions asked."""

        pool = EXCUSES.get(category, EXCUSES["work"])
        excuse = random.choice(pool)

        if category not in EXCUSES:
            raise HTTPException(
                  status_code = 404,
                  detail = f"Category {category} not found. Available categories {list(EXCUSES.keys())}"
            )

        return {
                 "category": category,
                 "urgency": urgency,
                 "excuse": f"{prefix[urgency]}{excuse}"
        }
@app.get("/categories")
def list_categoris(): 
        """See what you can get excuses for."""
        
        return {"categories": list(EXCUSES.keys())}

@app.get("/")
def root():
    return {
        "message": "ExcuseEngine API is running",
        "endpoints": ["/excuse", "/categories", "/docs"]
    }

@app.post("/excuse")
def post_excuse(request: ExcuseRequest):
    """Submit your situation, get your excuse."""

    if request.urgency < 1 or request.urgency > 3:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Urgency must be between 1 and 3")

    pool = EXCUSES.get(request.category, EXCUSES["work"])
    excuse = random.choice(pool)

    greeting = f"{request.name}, " if request.name else ""

    return {
        "category": request.category,
        "urgency": request.urgency,
        "excuse": f"{greeting}{prefix[request.urgency]}{excuse}"
    }
