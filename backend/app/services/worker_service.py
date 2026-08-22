"""
Worker service module for matching and executing tasks.
"""

import json
from pathlib import Path

from app.schemas.worker import WorkerProfile
from app.schemas.task import GeneratedTask

class WorkerService:
    def __init__(self) -> None:
        self.profiles: list[WorkerProfile] = []
        data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
        profiles_file = data_dir / 'worker_profiles.json'
        
        if profiles_file.exists():
            with open(profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both dict-style parsing depending on Pydantic version
                self.profiles = [WorkerProfile.model_validate(p) if hasattr(WorkerProfile, 'model_validate') else WorkerProfile.parse_obj(p) for p in data]
        else:
            self.profiles = []

    def get_workers(self) -> list[WorkerProfile]:
        return self.profiles

    def get_worker(self, worker_id: str) -> WorkerProfile | None:
        for profile in self.profiles:
            if profile.id == worker_id:
                return profile
        return None

    def match_worker(self, task: GeneratedTask) -> tuple[WorkerProfile, str]:
        if not self.profiles:
            raise ValueError("No worker profiles available.")

        # a. Filter by required_role (case-insensitive)
        role_matches = [
            p for p in self.profiles
            if p.role.lower() == task.required_role.lower()
        ]
        
        if not role_matches:
            # e. No perfect match for role, return closest match
            candidates = self.profiles
            reason_prefix = f"No worker with role '{task.required_role}' found. "
        else:
            candidates = role_matches
            reason_prefix = f"Matched role '{task.required_role}'. "

        # b. Filter by minimum_experience_years
        exp_matches = [
            p for p in candidates
            if p.experience_years >= task.minimum_experience_years
        ]
        
        if not exp_matches:
            # Fallback to candidates with the most experience
            candidates.sort(key=lambda x: x.experience_years, reverse=True)
            exp_matches = candidates
            reason_prefix += f"No worker meets {task.minimum_experience_years} years experience, using best available. "
        else:
            candidates = exp_matches
            reason_prefix += f"Meets experience requirement (>= {task.minimum_experience_years} years). "

        # c. Score remaining candidates by skill overlap
        best_candidate = None
        best_score = -1

        task_skills = set(skill.lower() for skill in task.required_skills)
        
        for p in candidates:
            worker_skills = set(skill.lower() for skill in p.skills)
            score = len(task_skills.intersection(worker_skills))
            
            # Deterministic tie-breaking: prefer more experience, then alphabetically by ID
            if score > best_score:
                best_score = score
                best_candidate = p
            elif score == best_score:
                if best_candidate is not None:
                    if p.experience_years > best_candidate.experience_years:
                        best_candidate = p
                    elif p.experience_years == best_candidate.experience_years:
                        if p.id < best_candidate.id:
                            best_candidate = p

        if best_candidate is None:
            best_candidate = candidates[0]

        reason = reason_prefix + f"Matched {best_score} required skills."
        return best_candidate, reason

    def match_workers_for_tasks(self, tasks: list[GeneratedTask]) -> list[tuple[GeneratedTask, WorkerProfile, str]]:
        results = []
        for task in tasks:
            worker, reason = self.match_worker(task)
            results.append((task, worker, reason))
        return results

_worker_service: WorkerService | None = None

def get_worker_service() -> WorkerService:
    global _worker_service
    if _worker_service is None:
        _worker_service = WorkerService()
    return _worker_service
