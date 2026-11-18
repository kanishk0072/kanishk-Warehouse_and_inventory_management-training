
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from tasks.welcome_email import simulate_welcome_email

from auth_dependencies import (
    get_current_user,
    credentials_exception,
)
from database import get_db
from models import User
from schemas.auth import (
    SignupRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
)
from schemas.user import UserResponse
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


# 1. SIGNUP
@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=201,
)
def signup(
    data: SignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    existing = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )p

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        name=data.name,
        email=email,
        hashed_password=get_password_hash(data.password),
        role="staff",
        warehouse_id=None,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    db.refresh(user)

    background_tasks.add_task(
        simulate_welcome_email,
        user.email,    
    )

    return user


# 2. LOGIN
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form_data.username.strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            user.token_version,
        ),
        refresh_token=create_refresh_token(
            user.id,
            user.token_version,
        ),
    )


# 3. REFRESH
@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(
            data.refresh_token,
            "refresh",
        )
    except InvalidTokenError:
        raise credentials_exception()

    user = db.get(User, int(payload["sub"]))

    if user is None:
        raise credentials_exception()

    if user.token_version != payload["ver"]:
        raise credentials_exception()

    return AccessTokenResponse(
        access_token=create_access_token(
            user.id,
            user.token_version,
        )
    )


# 4. LOGOUT
@router.post("/logout", status_code=204)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(
            token_version=User.token_version + 1
        )
    )

    db.commit()


# 5. CURRENT USER
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
