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

