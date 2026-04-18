from fastapi import FastAPI, Query
import random

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

@app.get("/excuse")
def get_excuse (
    category: str =Query(default="work", description= "work | gym | code | family"),
    urgency: int = Query(default=1, ge=1, le=3, description="1=chill, 3=desperate")
    ):
        """Returns a random excuse. No questions asked."""

        pool = EXCUSES.get(category, EXCUSES["work"])
        excuse = random.choice(pool)

        prefix = {
                1: "",
                2: "Look, honestly —  ",
                3: "I swear —"
        }

        return {
                 "category": category,
                 "urgency": urgency,
                 "excuse": f"{prefix[urgency]}{excuse}"
        }
@app.get("/categories")
def list_categoris(): 
        """See what you can get excuses for."""
        
        return {"categories": list(EXCUSES.keys())}
