from app.common.config import settings
from app.common.exceptions import ServiceException
from app.repositories.employee_repository import EmployeeRepository
from app.schemas import EmployeeCreateSchema
from app.schemas import EmployeeSchema
from app.schemas import EmployeeUpdateSchema
from app.schemas import EmployeeWithSkillsSchema
from app.schemas import ProfileCompletionSchema
from app.schemas import QuestEventSchema
from app.services.quest_service import QuestService


class EmployeeService:
    def __init__(self, repository: EmployeeRepository, quest_service: QuestService):
        self.repository = repository
        self.quest_service = quest_service
        self.MAX_SKILLS_FOR_EMPLOYEE = settings.MAX_SKILLS_FOR_EMPLOYEE

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
            employee_data = EmployeeWithSkillsSchema.model_validate(employee)
            return employee_data
        except Exception as e:
            raise ServiceException(f"Failed to get employee: {str(e)}") from e

    async def update_employee(
            self, employee_id: int, update_data: EmployeeUpdateSchema
    ) -> EmployeeSchema:
        """Update employee information"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            if not update_dict:
                raise ServiceException("No data provided for update")

            employee = await self.repository.update(employee_id, update_dict)

            completion = await self.calculate_completion(employee_id)

            await self.quest_service.handle_quest_event(QuestEventSchema(
                employee_id=employee_id,
                action_type="profile_update",
                count=1
            ))

            return EmployeeSchema.model_validate(employee)
        except Exception as e:
            raise ServiceException(f"Failed to update employee: {str(e)}") from e

    async def get_employee_profile(self, employee_id: int) -> EmployeeWithSkillsSchema:
        """Get employee profile (same as get by ID but with more context)"""
        return await self.get_employee_by_id(employee_id)

    async def calculate_completion(self, employee_id: int) -> ProfileCompletionSchema:
        """Calculate profile completion percentage for employee"""
        try:
            employee = await self.repository.get_employee_with_skills(employee_id)
            if not employee:
                raise ServiceException("Employee not found")
            completion_percentage = await self._calculate_completion_for_employee(employee)

            return ProfileCompletionSchema(
                completion_percentage=completion_percentage
            )
        except ServiceException:
            raise
        except Exception as e:
            raise ServiceException(f"Failed to calculate completion: {str(e)}") from e

    async def _calculate_completion_for_employee(self, employee) -> int:
        """Completion calculation based on field counts"""
        FIELD_WEIGHTS = {
            'first_name': 15,
            'last_name': 15,
            'email': 20,
            'department': 15,
            'rating': 15,
            'skills': 20,
        }
        fields_to_check = [
            ("first_name", lambda x: x and x.strip()),
            ("last_name", lambda x: x and x.strip()),
            ("email", lambda x: x and x.strip()),
            ("department", lambda x: x and x.strip()),
            ("rating", lambda x: x is not None and x >= 0),
        ]
        total_percentage = 0
        # Подсчет количества заполненных базовых полей
        for field_name, check_func in fields_to_check:
            field_value = getattr(employee, field_name, None)
            if check_func(field_value):
                total_percentage += FIELD_WEIGHTS.get(field_name, 0)

        # Проверка навыков
        skills_count = (
            len(employee.employee_skills) if hasattr(employee,'employee_skills') and employee.employee_skills else 0
        )

        # Навыки дают полный вес если их >= MAX_SKILLS_FOR_EMPLOYEE, иначе пропорционально
        if skills_count >= self.MAX_SKILLS_FOR_EMPLOYEE:
            total_percentage += FIELD_WEIGHTS['skills']
        else:
            skills_percentage = (skills_count / self.MAX_SKILLS_FOR_EMPLOYEE) * FIELD_WEIGHTS['skills']
            total_percentage += skills_percentage

        return min(100, int(round(total_percentage)))
