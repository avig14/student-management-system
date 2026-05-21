from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from api.auth.dependencies import create_access_token
from api.schemas import Token, UserCreate
from storage.database import DatabaseHandler

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_db():
    return DatabaseHandler()


@router.post("/register", status_code=201)
def register(user: UserCreate, db: DatabaseHandler = Depends(get_db)):
    if not user.username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty.")
    if not user.password:
        raise HTTPException(status_code=400, detail="Password cannot be empty.")
    if len(user.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    existing = db.fetch_user(user.username.strip())
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken.")
    hashed = pwd_context.hash(user.password)
    db.insert_user(user.username.strip(), hashed)
    return {"message": f"User '{user.username.strip()}' registered successfully."}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: DatabaseHandler = Depends(get_db)):
    user = db.fetch_user(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}
