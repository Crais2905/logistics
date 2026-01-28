from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.connector import Connector
from app.db.models import User

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD(Connector):
    def __init__(self):
        super().__init__(User)

    async def write_to_db(self, data, session: AsyncSession):
        hashed_password = password_context.hash(data.password)

        db_user = User(
            firstname=data.firstname,
            lastname=data.lastname,
            email=data.email,
            hashed_password=hashed_password
        )

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        return db_user

    async def get_user_by_email(
            self,
            user_email: str,
            session: AsyncSession,
    ):
        stmt = select(self.model).where(self.model.email == user_email)
        return await session.scalar(stmt)

    async def verify_password(
            self,
            password: str,
            hashed_password: str
  ):
        return password_context.verify(password, hashed_password)