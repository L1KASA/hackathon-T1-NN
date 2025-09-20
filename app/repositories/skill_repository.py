from typing import Optional

from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DatabaseException
from app.exceptions import IntegrityDataException
from app.models import Skill


class SkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, name: str, description: Optional[str] = None
    ) -> Skill:
        skill = Skill(name=name, description=description)
        try:
            self._session.add(skill)
            await self._session.commit()
            await self._session.refresh(skill)
            return skill
        except IntegrityError as e:
            await self._session.rollback()
            raise IntegrityDataException(str(e)) from e
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseException(f"Database operation failed: {str(e)}") from e
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Unexpected database error: {str(e)}") from e


    async def validate_skill_exists_by_name(self, name: str) -> bool:
        try:
            s_query = select(exists().where(Skill.name == name))
            result = await self._session.execute(s_query)
            return result.scalar()
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to validate skill existence: {str(e)}") from e
