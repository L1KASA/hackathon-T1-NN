from typing import Optional

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import DatabaseException
from app.common.exceptions import DuplicateEmployeeException
from app.common.exceptions import IntegrityDataException
from app.common.exceptions import NotFoundException
from app.models import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, employee_id: int) -> Employee:
        try:
            result = await self._session.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise NotFoundException("Employee", str(employee_id)) from None
            return employee
        except Exception as e:
            raise DatabaseException(str(e)) from e

    async def get_by_email(self, email: str) -> Optional[Employee]:
        try:
            result = await self._session.execute(
                select(Employee).where(Employee.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(str(e)) from e

    async def create(self, employee_data: dict) -> Employee:
        try:
            existing_employee = await self.get_by_email(employee_data["email"])
            if existing_employee:
                raise DuplicateEmployeeException(employee_data["email"])

            employee = Employee(**employee_data)
            self._session.add(employee)
            await self._session.commit()
            await self._session.refresh(employee)
            return employee
        except IntegrityError as e:
            await self._session.rollback()
            raise IntegrityDataException(str(e)) from e
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(str(e)) from e

    async def update(self, employee_id: int, update_data: dict) -> Employee:
        try:
            if "email" in update_data:
                existing_employee = await self.get_by_email(update_data["email"])
                if existing_employee:
                    raise DuplicateEmployeeException(update_data["email"])
            stmt = (
                update(Employee)
                .where(Employee.id == employee_id)
                .values(**update_data)
                .returning(Employee)
            )
            result = await self._session.execute(stmt)
            updated_employee = result.scalar_one()

            await self._session.commit()
            await self._session.refresh(updated_employee)
            return updated_employee
        except IntegrityError as e:
            await self._session.rollback()
            raise IntegrityDataException(f"Integrity error: {str(e)}") from e
        except DuplicateEmployeeException:
            await self._session.rollback()
            raise
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(f"Failed to update employee: {str(e)}") from e

    async def get_employee_with_skills(self, employee_id: int) -> Employee:
        try:
            query = (
                select(Employee)
                .options(selectinload(Employee.employee_skills))
                .where(Employee.id == employee_id)
            )
            result = await self._session.execute(query)
            employee = result.scalar_one_or_none()

            if not employee:
                raise NotFoundException("Employee", str(employee_id))

            return employee
        except Exception as e:
            raise DatabaseException(str(e)) from e

