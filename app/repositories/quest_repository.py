from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import DatabaseException
from app.common.exceptions import NotFoundException
from app.models import EmployeeQuest
from app.models import Quest


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_quest(self, quest_data: dict) -> Quest:
        try:
            quest = Quest(**quest_data)
            self._session.add(quest)
            await self._session.commit()
            await self._session.refresh(quest)
            return quest
        except IntegrityError as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to create quest: {str(e)}") from e

    async def get_all_quests(self) -> List[Quest]:
        try:
            query = select(Quest)
            result = await self._session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Failed to get quests: {str(e)}") from e

    async def get_quest_by_id(self, quest_id: int) -> Quest:
        try:
            result = await self._session.execute(
                select(Quest).where(Quest.id == quest_id)
            )
            quest = result.scalar_one_or_none()
            if not quest:
                raise NotFoundException("Quest", str(quest_id))
            return quest
        except Exception as e:
            raise DatabaseException(f"Failed to get quest: {str(e)}") from e

    async def get_quests_by_action_type(self, action_type: str) -> List[Quest]:
        try:
            result = await self._session.execute(
                select(Quest)
                .where(Quest.action_type == action_type)
                .where(Quest.is_active.is_(True))
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Failed to get quests by action type: {str(e)}") from e

    async def assign_quest_to_employee(self, employee_id: int, quest_id: int) -> EmployeeQuest:
        try:
            # Check if quest exists
            quest = await self.get_quest_by_id(quest_id)
            if not quest.is_active:
                raise DatabaseException("Cannot assign inactive quest")

            # Check if already assigned
            result = await self._session.execute(
                select(EmployeeQuest).where(
                    EmployeeQuest.employee_id == employee_id,
                    EmployeeQuest.quest_id == quest_id
                )
            )
            if result.scalar_one_or_none():
                raise DatabaseException("Quest already assigned to employee")

            employee_quest = EmployeeQuest(
                employee_id=employee_id,
                quest_id=quest_id,
                current_count=0,
                is_completed=False
            )
            self._session.add(employee_quest)
            await self._session.commit()
            await self._session.refresh(employee_quest)
            return employee_quest
        except IntegrityError as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to assign quest: {str(e)}") from e

    async def get_employee_quests(self, employee_id: int) -> List[EmployeeQuest]:
        try:
            result = await self._session.execute(
                select(EmployeeQuest)
                .where(EmployeeQuest.employee_id == employee_id)
                .options(selectinload(EmployeeQuest.quest))
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseException(f"Failed to get employee quests: {str(e)}") from e

    async def update_quest_progress(self, employee_id: int, action_type: str, count: int = 1) -> List[EmployeeQuest]:
        try:
            # Find all active quests for this employee with matching action type
            result = await self._session.execute(
                select(EmployeeQuest)
                .join(Quest)
                .where(
                    EmployeeQuest.employee_id == employee_id,
                    Quest.action_type == action_type,
                    EmployeeQuest.is_completed.is_(False),
                    Quest.is_active.is_(True)
                )
                .options(selectinload(EmployeeQuest.quest))
            )

            updated_quests = []
            for employee_quest in result.scalars().all():
                # Update progress
                new_count = min(employee_quest.current_count + count, employee_quest.quest.required_count)
                employee_quest.current_count = new_count

                # Check if completed
                if new_count >= employee_quest.quest.required_count:
                    employee_quest.is_completed = True

                updated_quests.append(employee_quest)

            await self._session.commit()
            return updated_quests
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to update quest progress: {str(e)}") from e

    async def get_quest_progress(self, employee_id: int, quest_id: int) -> EmployeeQuest:
        try:
            result = await self._session.execute(
                select(EmployeeQuest)
                .where(
                    EmployeeQuest.employee_id == employee_id,
                    EmployeeQuest.quest_id == quest_id
                )
                .options(selectinload(EmployeeQuest.quest))
            )
            quest_progress = result.scalar_one_or_none()
            if not quest_progress:
                raise NotFoundException("Quest progress", f"employee_{employee_id}_quest_{quest_id}")
            return quest_progress
        except Exception as e:
            raise DatabaseException(f"Failed to get quest progress: {str(e)}") from e


    async def update_percentage_quests(self, employee_id: int, action_type: str, percentage: int):
        """Update percentage quests with max logic"""
        try:
            result = await self._session.execute(
                select(EmployeeQuest)
                .join(Quest)
                .where(
                    EmployeeQuest.employee_id == employee_id,
                    Quest.action_type == action_type,
                    EmployeeQuest.is_completed(False),
                    Quest.is_active.is_(True)
                )
                .options(selectinload(EmployeeQuest.quest))
            )

            updated_quests = []
            for employee_quest in result.scalars().all():
                new_count = max(employee_quest.current_count, percentage)
                new_count = min(new_count, employee_quest.quest.required_count)

                employee_quest.current_count = new_count

                if new_count >= employee_quest.quest.required_count:
                    employee_quest.is_completed = True

                updated_quests.append(employee_quest)

            await self._session.commit()
            return updated_quests

        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to update percentage quests: {str(e)}") from e
