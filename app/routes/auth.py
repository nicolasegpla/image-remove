from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.models.user import User
from app.database.sesssion import get_db
from app.utils.security import get_password_hash, verify_password, create_access_token
import uuid
from app.core.config import settings
from uuid import UUID
from app.schemas.user_schema import UserUpdate
from app.services.user import get_user_tokens

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
     # ✅ Verifica que el código coincida
    if user.code_auth != settings.auth_code:
        raise HTTPException(status_code=401, detail="Invalid authorization code")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        id_api=str(uuid.uuid4()),
        email=user.email,
        password=get_password_hash(user.password),
        code_auth=user.code_auth,
        country=user.country,
        type_user="client",
        status=False,
        tokens=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": db_user.id,
        "email": db_user.email,
        "id_api": db_user.id_api,
        "status": db_user.status,
        "tokens": db_user.tokens,
        "type_user": db_user.type_user,
        "country": db_user.country,
    }}

# app/routes/auth.py (mismo archivo)



@router.put("/user/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizamos solo los campos que vienen en el payload
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@router.get("/users/{user_id}/tokens", response_model=int)
def get_user_tokens_endpoint(user_id: UUID, db: Session = Depends(get_db)):
    try:
        tokens = get_user_tokens(user_id, db)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))