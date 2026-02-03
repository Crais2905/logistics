from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.schemas.enums.enums import UserRole
from app.schemas.rout_schemas.user import UserCreate, UserPublic, UserLogin
from app.db.session import get_session
from app.crud.user import UserCRUD
from app.auth.tokens import create_access_token


router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def register_user(
    user_data: UserCreate,
    user_crud: UserCRUD = Depends(UserCRUD),
    session: AsyncSession = Depends(get_session)
):
    existing_user = await user_crud.get_user_by_email(user_data.email, session)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email already exist"
        )

    return await user_crud.write_to_db(user_data, session)


@router.post("/login/", status_code=status.HTTP_200_OK)
async def login_user(
    login_data: UserLogin,
    response: Response,
    user_crud: UserCRUD = Depends(UserCRUD),
    session: AsyncSession = Depends(get_session)
):
    user = await user_crud.get_user_by_email(login_data.email, session)

    if (not user) or (not await user_crud.verify_password(login_data.password, user.hashed_password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    response.set_cookie("access_token", access_token)

    return {
        "access_token": access_token
    }


@router.post("/logout/")
async def logout(
    response: Response
):
    response.delete_cookie("access_token")
    return {"Log out": "successful"}


@router.get("/me/", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def user_me(
    current_user: UserPublic = Depends(get_current_user)
):
    return current_user


@router.patch("/change-role/{user_id}", status_code=status.HTTP_200_OK)
async def change_user_role(
    user_id: UUID,
    new_role: UserRole,
    user_crud: UserCRUD = Depends(UserCRUD),
    session: AsyncSession = Depends(get_session),
    current_user: UserPublic = Depends(require_role(UserRole.admin)),
):
    user = await user_crud.get_object_by_id(user_id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = new_role.value
    await session.commit()
    await session.refresh(user)
