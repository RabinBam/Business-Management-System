from pydantic import BaseModel, Field


class WorkerProfile(BaseModel):
    id: str
    name: str
    role: str
    experience_years: float = Field(ge=0)
    skills: list[str] = Field(default_factory=list)


class WorkerResult(BaseModel):
    task_id: str
    worker_id: str
    summary: str
    output: dict[str, object] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)
    cost: float = Field(default=0, ge=0)
    assignment_reason: str = ""


class WorkerRead(WorkerProfile):
    department: str
    availability: str
    workload_percent: int = Field(ge=0, le=100)
    active_tasks: int = Field(ge=0)

