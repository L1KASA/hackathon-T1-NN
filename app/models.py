from typing import List
from typing import Optional

from sqlalchemy import TIMESTAMP
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


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
    level_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('levels.id'),
        nullable=True,
        comment="Current level ID of the employee"
    )
    total_xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="Total experience points earned by the employee"
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

    # Relationships
    employee_skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    experience_records: Mapped[List["ExperiencePoints"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    current_level: Mapped[Optional["Level"]] = relationship(back_populates="employees")
    rewards_earned: Mapped[List["EmployeeReward"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    quests_progress: Mapped[List["EmployeeQuest"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    roadmaps_progress: Mapped[List["EmployeeRoadmap"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    leaderboard_entries: Mapped[List["LeaderboardEntry"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    tips_sent: Mapped[List["Tip"]] = relationship(
        foreign_keys="Tip.from_employee_id",
        back_populates="from_employee"
    )
    tips_received: Mapped[List["Tip"]] = relationship(
        foreign_keys="Tip.to_employee_id",
        back_populates="to_employee"
    )
    project_teams: Mapped[List["ProjectTeam"]] = relationship(back_populates="employee")


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
    project_requirements: Mapped[List["ProjectRequiredSkill"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan"
    )


class ExperiencePoints(Base):
    """Experience points earned by employees for various actions"""
    __tablename__ = 'experience_points'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the experience record"
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee who earned the points"
    )
    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of experience points earned"
    )
    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of action that earned the points (profile_update, skill_add, etc.)"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the skill was created",
    )
    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="experience_records")


class Level(Base):
    """Experience levels for gamification system"""
    __tablename__ = 'levels'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the level"
    )
    level_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Name of the level (e.g., Novice, Explorer, Expert, Leader)"
    )
    min_xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Minimum experience points required to reach this level"
    )
    badge_url: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="URL to the level badge image"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of the level and its privileges"
    )
    # Relationships
    employees: Mapped[List["Employee"]] = relationship(back_populates="current_level")


class Reward(Base):
    """Universal reward system for all types of awards"""
    __tablename__ = 'rewards'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the reward"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Name of the reward"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the reward and how to earn it"
    )
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Type of reward: virtual, career, real"
    )
    subtype: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Subtype: badge, avatar, profile_theme, career_opportunity, physical_item"
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="URL to reward image (for badges, avatars, etc)"
    )
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Experience points awarded with this reward"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether the reward is currently available"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the reward was created"
    )
    # Relationships
    employee_rewards: Mapped[List["EmployeeReward"]] = relationship(back_populates="reward")


class EmployeeReward(Base):
    """Association table for employees and rewards they've earned"""
    __tablename__ = 'employee_rewards'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the employee-reward association"
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee who earned the reward"
    )
    reward_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('rewards.id', ondelete="CASCADE"),
        comment="ID of the reward that was earned"
    )
    earned_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the reward was earned"
    )
    is_claimed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether the reward has been claimed (for real rewards)"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the skill was created",
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="rewards_earned")
    reward: Mapped["Reward"] = relationship(back_populates="employee_rewards")


class Quest(Base):
    """Gamified quests or missions for employees to complete"""
    __tablename__ = 'quests'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the quest"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Name of the quest"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description of the quest objectives"
    )
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Experience points awarded for completing the quest"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether the quest is currently available"
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    required_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the skill was created",
    )
    roadmap_links: Mapped[List["RoadmapQuest"]] = relationship(back_populates="quest")
    employee_quests: Mapped[List["EmployeeQuest"]] = relationship(back_populates="quest")


class EmployeeQuest(Base):
    """Progress tracking for employees on quests"""
    __tablename__ = 'employee_quests'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the employee quest progress"
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee working on the quest"
    )
    quest_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('quests.id', ondelete="CASCADE"),
        comment="ID of the quest"
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether the quest has been completed"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the quest was created",
    )
    current_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Current progress count for the quest action"
    )
    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="quests_progress")
    quest: Mapped["Quest"] = relationship(back_populates="employee_quests")


class RoadmapQuest(Base):
    __tablename__ = 'roadmap_quests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(
        ForeignKey('career_roadmaps.id', ondelete="CASCADE"),
        comment="ID of the career roadmap"
    )
    quest_id: Mapped[int] = mapped_column(
        ForeignKey('quests.id', ondelete="CASCADE"),
        comment="ID of the quest"
    )
    importance: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        comment="How important this quest is for the roadmap (0-1)"
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether this quest is required to complete the roadmap"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the association was created"
    )
    # Relationships
    roadmap: Mapped["CareerRoadmap"] = relationship(back_populates="quest_links")
    quest: Mapped["Quest"] = relationship(back_populates="roadmap_links")


class CareerRoadmap(Base):
    """Career progression paths for employees"""
    __tablename__ = 'career_roadmaps'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    # Relationships
    required_skills: Mapped[List["RoadmapRequiredSkill"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan"
    )
    employee_roadmaps: Mapped[List["EmployeeRoadmap"]] = relationship(back_populates="roadmap")
    quest_links: Mapped[List["RoadmapQuest"]] = relationship(back_populates="roadmap")


class RoadmapRequiredSkill(Base):
    __tablename__ = 'roadmap_required_skills'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey('career_roadmaps.id', ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey('skills.id', ondelete="CASCADE"))
    required_level: Mapped[int] = mapped_column(Integer, nullable=False)

    roadmap: Mapped["CareerRoadmap"] = relationship(back_populates="required_skills")
    skill: Mapped["Skill"] = relationship()


class EmployeeRoadmap(Base):
    """Employee progress on career roadmaps"""
    __tablename__ = 'employee_roadmaps'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the employee roadmap progress"
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee following the roadmap"
    )
    roadmap_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('career_roadmaps.id', ondelete="CASCADE"),
        comment="ID of the career roadmap"
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        comment="Percentage of roadmap completion (0-100)"
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether the roadmap has been completed"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the employee roadmap was created",
    )
    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="roadmaps_progress")
    roadmap: Mapped["CareerRoadmap"] = relationship(back_populates="employee_roadmaps")


class Leaderboard(Base):
    """Gamification leaderboards for different periods and criteria"""
    __tablename__ = 'leaderboards'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the leaderboard"
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Name of the leaderboard"
    )
    period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Time period of the leaderboard (weekly, monthly, all-time)"
    )
    criteria: Mapped[List["LeaderboardCriterion"]] = relationship(
        back_populates="leaderboard", cascade="all, delete-orphan"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Whether the leaderboard is currently active"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the leaderboard was created",
    )
    # Relationships
    entries: Mapped[List["LeaderboardEntry"]] = relationship(back_populates="leaderboard")


class LeaderboardCriterion(Base):
    __tablename__ = 'leaderboard_criteria'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    leaderboard_id: Mapped[int] = mapped_column(ForeignKey('leaderboards.id', ondelete="CASCADE"))
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    leaderboard: Mapped["Leaderboard"] = relationship(back_populates="criteria")


class LeaderboardEntry(Base):
    """Individual entries in leaderboards"""
    __tablename__ = 'leaderboard_entries'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the leaderboard entry"
    )
    leaderboard_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('leaderboards.id', ondelete="CASCADE"),
        comment="ID of the leaderboard"
    )
    employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee on the leaderboard"
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Calculated score based on leaderboard criteria"
    )
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Current rank position on the leaderboard"
    )
    # Relationships
    leaderboard: Mapped["Leaderboard"] = relationship(back_populates="entries")
    employee: Mapped["Employee"] = relationship(back_populates="leaderboard_entries")


class Tip(Base):
    """System for colleagues to tip each other"""
    __tablename__ = 'tips'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        comment="Unique identifier of the tip record"
    )
    from_employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee sending the tip"
    )
    to_employee_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('employees.id', ondelete="CASCADE"),
        comment="ID of the employee receiving the tip"
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Tip message from the sender"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the tip was created",
    )
    # Relationships
    from_employee: Mapped["Employee"] = relationship(
        foreign_keys=[from_employee_id],
        back_populates="tips_sent"
    )
    to_employee: Mapped["Employee"] = relationship(
        foreign_keys=[to_employee_id],
        back_populates="tips_received"
    )


class Project(Base):
    """Table of projects"""
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    required_level: Mapped[str] = mapped_column(String(50), nullable=True)  # Junior/Middle/Senior
    status: Mapped[str] = mapped_column(String(20), default='active')  # active, completed, cancelled
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())
    # Relationships
    team_members: Mapped[List["ProjectTeam"]] = relationship(back_populates="project")
    required_skills_links: Mapped[List["ProjectRequiredSkill"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )


class ProjectRequiredSkill(Base):
    """Required skills for projects"""
    __tablename__ = 'project_required_skills'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey('projects.id', ondelete="CASCADE"),
        comment="ID of the project"
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey('skills.id', ondelete="CASCADE"),
        comment="ID of the required skill"
    )
    required_level: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Required proficiency level for this skill (optional)"
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        comment="Date and time when the requirement was created"
    )

    project: Mapped["Project"] = relationship(back_populates="required_skills_links")
    skill: Mapped["Skill"] = relationship(back_populates="project_requirements")


class ProjectTeam(Base):
    """Table of team members"""
    __tablename__ = 'project_teams'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete="CASCADE"))
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id', ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(100), nullable=True, comment="Role assigned to the team")
    joined_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="team_members")
    employee: Mapped["Employee"] = relationship(back_populates="project_teams")
