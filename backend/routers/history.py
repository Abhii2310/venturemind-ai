from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
import json

from database import get_db
from models import StartupHistory, User
from auth_utils import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/history", tags=["history"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class HistoryItem(BaseModel):
    id: int
    idea: str
    summary: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class HistoryDetail(BaseModel):
    id: int
    idea: str
    full_json: dict
    created_at: str

    class Config:
        orm_mode = True

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/", response_model=List[HistoryItem])
def get_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(StartupHistory).filter(StartupHistory.user_id == current_user.id).order_by(StartupHistory.created_at.desc()).all()

@router.get("/{item_id}", response_model=HistoryDetail)
def get_history_detail(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(StartupHistory).filter(StartupHistory.id == item_id, StartupHistory.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")
    
    # Parse the JSON string back to dict
    return {
        "id": item.id,
        "idea": item.idea,
        "full_json": json.loads(item.full_json),
        "created_at": str(item.created_at)
    }
