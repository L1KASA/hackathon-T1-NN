from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from starlette import status

from app.common.exceptions import DatabaseException
from app.common.exceptions import DuplicateEmployeeException
from app.common.exceptions import IntegrityDataException
from app.common.exceptions import NotFoundException
from app.dependencies import get_employee_service
from app.schemas import EmployeeCreateSchema
from app.schemas import EmployeeSchema
from app.schemas import EmployeeUpdateSchema
from app.schemas import EmployeeWithSkillsSchema
from app.services.employee_service import EmployeeService

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)

# Simple token validation (in real app use JWT or similar)
security = HTTPBearer()

async def get_current_employee_id(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Extract employee ID from token (simplified)"""
    # In real application, decode JWT token and extract employee ID
    try:
        # This is a simplified example - in production use proper JWT validation
        employee_id = int(credentials.credentials)
        return employee_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) from None

@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreateSchema,
    service: EmployeeService = Depends(get_employee_service),
):
    """Create a new employee"""
    try:
        employee = await service.create_employee(employee_data)
        return employee
    except DuplicateEmployeeException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        ) from None
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get("/me", response_model=EmployeeWithSkillsSchema)
async def get_employee_profile(
    employee_id: int = Depends(get_current_employee_id),
    service: EmployeeService = Depends(get_employee_service),
):
    """Get current employee profile"""
    try:
        employee = await service.get_employee_profile(employee_id)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.put("/{employee_id}", response_model=EmployeeSchema)
async def update_employee(
    employee_id: int,
    update_data: EmployeeUpdateSchema,
    service: EmployeeService = Depends(get_employee_service),
):
    """Update employee information"""
    try:
        employee = await service.update_employee(employee_id, update_data)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except (DatabaseException, IntegrityDataException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None

@router.get("/{employee_id}", response_model=EmployeeWithSkillsSchema)
async def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    """Get employee by ID"""
    try:
        employee = await service.get_employee_by_id(employee_id)
        return employee
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from None
