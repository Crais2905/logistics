from  fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserCRUD
from app.db.session import get_session
from app.auth.tokens import decode_token
from app.schemas.rout_schemas.user import UserPublic


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user_crud: UserCRUD = Depends(UserCRUD),
):
    try:
        token = request.cookies.get("access_token")
        payload = decode_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await user_crud.get_user_by_email(email, session)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_role(*allowed_role):
    allowed_role = {role.value for role in allowed_role}

    async def role_checker(
        current_user: UserPublic = Depends(get_current_user)
    ):
        if current_user.role not in allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user

    return role_checker
