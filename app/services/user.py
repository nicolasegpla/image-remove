from sqlalchemy import UUID
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate
from passlib.context import CryptContext
import uuid
from datetime import datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user_data: UserCreate) -> User:
    db_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password=hash_password(user_data.password),
        code_auth=user_data.code_auth,
        id_api=str(uuid.uuid4()),
        status=False,
        tokens=0,
        type_user="client",
        country=user_data.country,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def get_user_tokens(user_id: UUID, db: Session) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    return user.tokens