from fastapi import Depends
from decouple import config
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, delete
from sqlalchemy.orm import selectinload


class Connector:
    def __init__(self, model):
        self.model = model

    async def write_to_db(self, data, session: AsyncSession):
        stmt = insert(self.model).values(data.model_dump()).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()

        return result

    async def get_object_by_id(
            self, obj_id: UUID,
            session: AsyncSession,
            selection_fields: list = None
    ):
        stmt = select(self.model).where(self.model.id == obj_id)

        if selection_fields is not None:
            for field in selection_fields:
                stmt = stmt.options(selectinload(getattr(self.model, field)))

        return await session.scalar(stmt)