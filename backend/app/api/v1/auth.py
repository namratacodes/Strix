from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.api.v1.schemas import UserResponse
from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.domain.entities import User
from app.infrastructure.auth.google_oauth import build_oauth_client
from app.infrastructure.persistence.sqlalchemy_user_repository import SqlAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request, settings: Settings = Depends(get_settings)):
    oauth = build_oauth_client(settings)
    return await oauth.google.authorize_redirect(request, settings.google_redirect_uri)


@router.get("/callback")
async def callback(
    request: Request,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
):
    oauth = build_oauth_client(settings)
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo") or await oauth.google.userinfo(token=token)

    repo = SqlAlchemyUserRepository(db)
    user = repo.get_or_create_by_google_id(
        google_id=userinfo["sub"],
        email=userinfo["email"],
        display_name=userinfo.get("name", userinfo["email"]),
    )
    request.session["user_id"] = str(user.id)
    return RedirectResponse(url=f"{settings.frontend_url}/analyze")


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, display_name=user.display_name)


@router.post("/logout")
async def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"status": "logged_out"}