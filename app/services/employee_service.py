from app.exceptions import ServiceException
from app.repositories.employee_repository import EmployeeRepository
from app.schemas import EmployeeCreateSchema
from app.schemas import EmployeeSchema
from app.schemas import EmployeeUpdateSchema
from app.schemas import EmployeeWithSkillsSchema


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def create_employee(self, employee_data: EmployeeCreateSchema) -> EmployeeSchema:
        """Create a new employee"""
        try:
            employee_dict = employee_data.model_dump()
            employee = await self.repository.create(employee_dict)
            return EmployeeSchema.model_validate(employee)
        except Exception as e:
            raise ServiceException(f"Failed to create employee: {str(e)}") from e

    async def get_employee_by_id(self, employee_id: int) -> EmployeeWithSkillsSchema:
        """Get employee by ID with skills"""
        try:
            employee = await self.repository.get_employee_with_skills(employee_id)

            # Convert skills to schema format
            skills_data = []
            for emp_skill in employee.employee_skills:
                skills_data.append({
                    "skill_id": emp_skill.skill_id,
                    "proficiency_level": emp_skill.proficiency_level
                })

            employee_data = EmployeeWithSkillsSchema.model_validate(employee)
            employee_data.skills = skills_data
            return employee_data
        except Exception as e:
            raise ServiceException(f"Failed to get employee: {str(e)}") from e

    async def update_employee(self, employee_id: int, update_data: EmployeeUpdateSchema) -> EmployeeSchema:
        """Update employee information"""
        try:
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            if not update_dict:
                raise ServiceException("No data provided for update")

            employee = await self.repository.update(employee_id, update_dict)
            return EmployeeSchema.model_validate(employee)
        except Exception as e:
            raise ServiceException(f"Failed to update employee: {str(e)}") from e

    async def get_employee_profile(self, employee_id: int) -> EmployeeWithSkillsSchema:
        """Get employee profile (same as get by ID but with more context)"""
        return await self.get_employee_by_id(employee_id)
