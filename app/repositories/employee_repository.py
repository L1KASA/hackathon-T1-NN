from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import DatabaseException
from app.exceptions import DuplicateEmployeeException
from app.exceptions import IntegrityDataException
from app.exceptions import NotFoundException
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

    async def get_by_email(self, email: str) -> Employee:
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
            employee = await self.get_by_id(employee_id)

            for key, value in update_data.items():
                setattr(employee, key, value)

            await self._session.commit()
            await self._session.refresh(employee)
            return employee
        except IntegrityError as e:
            await self._session.rollback()
            raise IntegrityDataException(str(e)) from e
        except Exception as e:
            await self._session.rollback()
            raise DatabaseException(str(e)) from e

    async def get_employee_with_skills(self, employee_id: int) -> Employee:
        try:
            result = await self._session.execute(
                select(Employee)
                .where(Employee.id == employee_id)
                .options(selectinload(Employee.employee_skills))
            )
            employee = result.scalar_one_or_none()
            if not employee:
                raise NotFoundException("Employee", str(employee_id)) from None
            return employee
        except Exception as e:
            raise DatabaseException(str(e)) from e
