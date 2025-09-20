from typing import Optional

from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import IntegrityDataException, DatabaseException
from app.models import Skill


class SkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_skill(
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
            raise IntegrityDataException(str(e))
        except SQLAlchemyError as e:
            await self._session.rollback()
            raise DatabaseException(f"Database operation failed: {str(e)}")
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Unexpected database error: {str(e)}")


    async def validate_skill_exists_by_name(self, name: str) -> bool:
        try:
            s_query = select(exists().where(Skill.name == name))
            result = await self._session.execute(s_query)
            return result.scalar()
        except SQLAlchemyError as e:
            raise DatabaseException(f"Failed to validate skill existence: {str(e)}")
