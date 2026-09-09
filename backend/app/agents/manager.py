import json
from collections.abc import Iterable, Mapping

from pydantic import BaseModel

from app.schemas.marketing import MarketingPlan
from app.schemas.report import Report
from app.schemas.task import GeneratedTask, GeneratedTaskList, ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import ExecutiveSummary, WorkflowRead
from app.services.ai_service import AIService, MockAIProvider, get_ai_service


class ReviewBatch(BaseModel):
    reviews: list[ManagementReview]


REFINE_SYSTEM_PROMPT = """You are the Byapari management planning reviewer.
Refine one planned task so it is unambiguous, assignable, and measurable.
You may adjust role, experience, skills, difficulty, output, and acceptance
criteria. Preserve the dependency_task_ids exactly. Do not execute the task."""

REVIEW_SYSTEM_PROMPT = """You are the Byapari management quality reviewer.
Compare one worker result with its task and acceptance criteria. Return either
APPROVED or REVISION_REQUIRED. A revision decision must contain actionable
revision instructions. Do not rewrite or perform the worker's task."""

SUMMARY_SYSTEM_PROMPT = """You are the Byapari executive reporting manager.
Create a concise executive summary using only the approved workflow, report,
marketing plan, and management reviews supplied. Do not invent metrics, access,
or completed work. Separate facts, risks, and the management recommendation."""


class ManagementError(RuntimeError):
    """Raised when management output violates a deterministic contract."""


class Manager:
    def __init__(self, ai_service: AIService, *, model: str | None = None) -> None:
        self._ai_service = ai_service
        self._model = model

    async def refine_plan(self, tasks: list[GeneratedTask]) -> list[GeneratedTask]:
        plan = await self._ai_service.generate_structured(
            system_prompt=(
                "Review this entire Byapari task plan. Keep task order, exact roles, "
                "and dependencies unchanged. Make descriptions, employee briefings, "
                "acceptance criteria and department handoffs useful and concise. "
                "Do not add tasks or execute work. Preserve experience tailoring."
            ),
            user_prompt=GeneratedTaskList(tasks=tasks).model_dump_json(),
            schema=GeneratedTaskList,
            model=self._model,
        )
        if len(plan.tasks) != len(tasks) or any(
            a.required_role != b.required_role or a.dependency_task_ids != b.dependency_task_ids
            for a, b in zip(tasks, plan.tasks, strict=True)
        ):
            raise ManagementError("Plan review changed assignments or dependencies")
        return plan.tasks

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
            "TASK_JSON:\n" + task.model_dump_json() + "\nRESULT_JSON:\n" + result.model_dump_json()
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
        results = list(results)
        if not isinstance(self._ai_service, MockAIProvider):
            result_ids = [r.task_id for r in results]
            if len(result_ids) != len(set(result_ids)) or set(result_ids) != set(tasks_by_id):
                raise ManagementError("Worker results must cover all tasks exactly once")
            batch = await self._ai_service.generate_structured(
                system_prompt=REVIEW_SYSTEM_PROMPT
                + (
                    " Review all submissions in one response, exactly once per task. "
                    "Assess the requested deliverable, not whether a real-world launch has "
                    "already happened. Never approve a mere claim of completion without evidence."
                ),
                user_prompt=json.dumps(
                    [
                        {
                            "task_id": r.task_id,
                            "expected_output": tasks_by_id[r.task_id].expected_output,
                            "acceptance_criteria": tasks_by_id[r.task_id].acceptance_criteria,
                            "submission": str(r.output.get("deliverable", r.summary))[:8000],
                        }
                        for r in results
                    ]
                ),
                schema=ReviewBatch,
                model=self._model,
            )
            ids = [r.task_id for r in batch.reviews]
            if len(ids) != len(set(ids)) or set(ids) != set(tasks_by_id):
                raise ManagementError("Management must review every task exactly once")
            return batch.reviews
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
            raise ManagementError("Worker results are missing for: " + ", ".join(sorted(missing)))
        return reviews

    async def create_executive_summary(
        self,
        *,
        workflow: WorkflowRead,
        report: Report,
        marketing: MarketingPlan,
        reviews: Iterable[ManagementReview],
        results: Iterable[WorkerResult] = (),
    ) -> ExecutiveSummary:
        if report.workflow_id != workflow.id or marketing.workflow_id != workflow.id:
            raise ManagementError("Summary inputs do not belong to the workflow")
        context: Mapping[str, object] = {
            "workflow": workflow.model_dump(mode="json", exclude={"executive_summary"}),
            "report": report.model_dump(mode="json"),
            "marketing": marketing.model_dump(mode="json"),
            "management_reviews": [review.model_dump(mode="json") for review in reviews],
            "employee_deliverables": [
                {
                    "task_id": r.task_id,
                    "worker_id": r.worker_id,
                    "deliverable": str(r.output.get("deliverable", r.summary))[:3000],
                }
                for r in results
            ],
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
    return await Manager(ai_service or get_ai_service(), model=model).review_worker_result(
        task=task, result=result
    )


async def create_executive_summary(
    *,
    workflow: WorkflowRead,
    report: Report,
    marketing: MarketingPlan,
    reviews: Iterable[ManagementReview],
    ai_service: AIService | None = None,
    model: str | None = None,
) -> ExecutiveSummary:
    return await Manager(ai_service or get_ai_service(), model=model).create_executive_summary(
        workflow=workflow,
        report=report,
        marketing=marketing,
        reviews=reviews,
    )
