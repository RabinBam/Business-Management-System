<<<<<<< HEAD
"""Person 1 starting point: task refinement, review, and executive summary."""

=======
import json
from collections.abc import Iterable, Mapping

from app.schemas.marketing import MarketingPlan
from app.schemas.report import Report
from app.schemas.task import GeneratedTask, ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import ExecutiveSummary, WorkflowRead
from app.services.ai_service import AIService, get_ai_service

REFINE_SYSTEM_PROMPT = """You are the AegisFlow management planning reviewer.
Refine one planned task so it is unambiguous, assignable, and measurable.
You may adjust role, experience, skills, difficulty, output, and acceptance
criteria. Preserve the dependency_task_ids exactly. Do not execute the task."""

REVIEW_SYSTEM_PROMPT = """You are the AegisFlow management quality reviewer.
Compare one worker result with its task and acceptance criteria. Return either
APPROVED or REVISION_REQUIRED. A revision decision must contain actionable
revision instructions. Do not rewrite or perform the worker's task."""

SUMMARY_SYSTEM_PROMPT = """You are the AegisFlow executive reporting manager.
Create a concise executive summary using only the approved workflow, report,
marketing plan, and management reviews supplied. Do not invent metrics, access,
or completed work. Separate facts, risks, and the management recommendation."""


class ManagementError(RuntimeError):
    """Raised when management output violates a deterministic contract."""


class Manager:
    def __init__(self, ai_service: AIService, *, model: str | None = None) -> None:
        self._ai_service = ai_service
        self._model = model

    async def refine_task(self, task: GeneratedTask) -> GeneratedTask:
        refined = await self._ai_service.generate_structured(
            system_prompt=REFINE_SYSTEM_PROMPT,
            user_prompt="TASK_JSON:\n" + task.model_dump_json(),
            schema=GeneratedTask,
            model=self._model,
        )
        if refined.dependency_task_ids != task.dependency_task_ids:
            raise ManagementError("Management refinement changed task dependencies")
        return refined

    async def review_worker_result(
        self,
        *,
        task: TaskRead,
        result: WorkerResult,
    ) -> ManagementReview:
        if result.task_id != task.id:
            raise ManagementError("Worker result does not belong to the supplied task")
        prompt = (
            "TASK_JSON:\n"
            + task.model_dump_json()
            + "\nRESULT_JSON:\n"
            + result.model_dump_json()
        )
        review = await self._ai_service.generate_structured(
            system_prompt=REVIEW_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema=ManagementReview,
            model=self._model,
        )
        if review.task_id != task.id:
            raise ManagementError("Management review returned a mismatched task ID")
        return review

    async def review_results(
        self,
        *,
        tasks: Iterable[TaskRead],
        results: Iterable[WorkerResult],
    ) -> list[ManagementReview]:
        tasks_by_id = {task.id: task for task in tasks}
        reviews: list[ManagementReview] = []
        seen_results: set[str] = set()

        for result in results:
            if result.task_id in seen_results:
                raise ManagementError(f"Duplicate worker result for {result.task_id}")
            task = tasks_by_id.get(result.task_id)
            if task is None:
                raise ManagementError(f"Worker result references unknown task {result.task_id}")
            reviews.append(await self.review_worker_result(task=task, result=result))
            seen_results.add(result.task_id)

        missing = set(tasks_by_id) - seen_results
        if missing:
            raise ManagementError(
                "Worker results are missing for: " + ", ".join(sorted(missing))
            )
        return reviews

    async def create_executive_summary(
        self,
        *,
        workflow: WorkflowRead,
        report: Report,
        marketing: MarketingPlan,
        reviews: Iterable[ManagementReview],
    ) -> ExecutiveSummary:
        if report.workflow_id != workflow.id or marketing.workflow_id != workflow.id:
            raise ManagementError("Summary inputs do not belong to the workflow")
        context: Mapping[str, object] = {
            "workflow": workflow.model_dump(mode="json", exclude={"executive_summary"}),
            "report": report.model_dump(mode="json"),
            "marketing": marketing.model_dump(mode="json"),
            "management_reviews": [review.model_dump(mode="json") for review in reviews],
        }
        summary = await self._ai_service.generate_structured(
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            user_prompt="SUMMARY_CONTEXT:\n" + json.dumps(context, ensure_ascii=False),
            schema=ExecutiveSummary,
            model=self._model,
        )
        return summary.model_copy(update={"objective": workflow.objective})


async def refine_task(
    task: GeneratedTask,
    *,
    ai_service: AIService | None = None,
    model: str | None = None,
) -> GeneratedTask:
    return await Manager(ai_service or get_ai_service(), model=model).refine_task(task)


async def review_worker_result(
    *,
    task: TaskRead,
    result: WorkerResult,
    ai_service: AIService | None = None,
    model: str | None = None,
) -> ManagementReview:
    return await Manager(
        ai_service or get_ai_service(), model=model
    ).review_worker_result(task=task, result=result)


async def create_executive_summary(
    *,
    workflow: WorkflowRead,
    report: Report,
    marketing: MarketingPlan,
    reviews: Iterable[ManagementReview],
    ai_service: AIService | None = None,
    model: str | None = None,
) -> ExecutiveSummary:
    return await Manager(
        ai_service or get_ai_service(), model=model
    ).create_executive_summary(
        workflow=workflow,
        report=report,
        marketing=marketing,
        reviews=reviews,
    )
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
