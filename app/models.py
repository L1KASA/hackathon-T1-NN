from sqlalchemy import BigInteger, Float, TIMESTAMP, func, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sqlalchemy.orm import relationship

Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the employee",
    )
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Email address of the employee"
    )
    first_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="First name of the employee"
    )
    last_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Last name of the employee"
    )
    department: Mapped[str] = mapped_column(
        String, comment="Department of the employee", nullable=True
    )
    rating: Mapped[float] = mapped_column(
        Float, default=0, nullable=False, comment="Rating of the employee"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the employee was created",
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        onupdate=func.current_timestamp(),
        comment="Date and time when the employee was last updated",
    )
    employee_skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class EmployeeSkill(Base):
    __tablename__ = 'employee_skills'

    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        primary_key=True,
        comment="Id of the employee",
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('skills.id', ondelete="CASCADE"),
        primary_key=True,
        comment="Id of the skill",
    )
    proficiency_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Proficiency level of the skill",
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the employee skill was created",
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="employee_skills")
    skills: Mapped["Skill"] = relationship(back_populates="employee_skills")

class Skill(Base):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the skill",
    )
    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Name of the skill"
    )
    description: Mapped[str] = mapped_column(
        Text, comment="Description of the skill", nullable=True
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the skill was created",
    )

    # Relationships
    employee_skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="skills",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
