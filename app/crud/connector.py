from fastapi import Depends

from decouple import config
from typing import Any, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, delete, update
from sqlalchemy.orm import selectinload, InstrumentedAttribute


class Connector:
    def __init__(self, model):
        self.model = model

    async def write_to_db(self, data, session: AsyncSession):
        stmt = insert(self.model).values(data.model_dump()).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()

        return result.scalar()

    async def get_objects(
            self,
            session: AsyncSession,
            offset: int = 0,
            limit: int = 10,
            filters: list | None = None,
    ):
        stmt = select(self.model)

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.offset(offset).limit(limit)
        return await session.scalars(stmt)

    async def get_object_by_unic_field(
        self, field_value,
        field: InstrumentedAttribute,
        session: AsyncSession,
        selection_fields: list[InstrumentedAttribute] | None = None
    ):
        stmt = select(self.model).where(field == field_value)

        if selection_fields is not None:
            for s_field in selection_fields:
                stmt = stmt.options(selectinload(s_field))

        return await session.scalar(stmt)

    async def update_object(
            self, object_id: UUID,
            new_values,
            session: AsyncSession
    ):
        values = new_values.model_dump(exclude_unset=True)
        stmt = update(self.model).where(self.model.id == object_id).values(values).returning(self.model)
        result = await session.execute(stmt)
        await session.commit()

        return result.scalar()

    async def deactivate_object(
        self, object_id: UUID,
        session: AsyncSession
    ):
        obj = await self.get_object_by_unic_field(
            object_id,
            self.model.id,
            session
        )

        obj.is_active = False
        await session.commit()
        await session.refresh(obj)

