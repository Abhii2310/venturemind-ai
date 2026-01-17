from typing import Any, Dict, Optional
import json

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import jwt

from venture_chain import get_venture_response
from database import engine, Base, get_db
import models
from routers import auth, history
from auth_utils import SECRET_KEY, ALGORITHM

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VentureMind.AI Backend",
    description="Backend API for VentureMind.AI startup co-founder chatbot.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; you can restrict later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(history.router)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply_markdown: str
    startup_pack: Dict[str, Any]
    domains: list = []
    competitor_matrix: list = []

def get_optional_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    except Exception:
        return None

@app.get("/")
def read_root():
    return {"status": "ok", "message": "VentureMind.AI backend running."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest, 
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_optional_user)
):
    try:
        result = await get_venture_response(payload.message)
        
        # Save to history if user is logged in
        if user:
            startup_pack = result.get("startup_pack", {})
            summary = startup_pack.get("startup_summary", "")
            
            history_item = models.StartupHistory(
                user_id=user.id,
                idea=payload.message,
                summary=summary,
                full_json=json.dumps(startup_pack)
            )
            db.add(history_item)
            db.commit()

        return ChatResponse(
            reply_markdown=result["reply_markdown"],
            startup_pack=result["startup_pack"],
            domains=result.get("domains", []),
            competitor_matrix=result.get("competitor_matrix", [])
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
