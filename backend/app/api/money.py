from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.database import get_json_store
from app.schemas.common import ApiResponse
from app.services.worker_service import get_worker_service
from app.services.workflow_service import get_workflow_service

router = APIRouter(prefix="/money", tags=["money"])


class MoneyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kind: Literal["income", "expense"]
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=3, max_length=300)
    date: date
    workflow_id: str | None = None
    worker_id: str | None = None


@router.get("")
async def money():
    entries = [v for _, v in get_json_store().list("money")]
    income = sum((Decimal(e["amount"]) for e in entries if e["kind"] == "income"), Decimal(0))
    expenses = sum((Decimal(e["amount"]) for e in entries if e["kind"] == "expense"), Decimal(0))
    return ApiResponse(
        data={
            "entries": list(reversed(entries)),
            "income": str(income),
            "expenses": str(expenses),
            "net": str(income - expenses),
        }
    )


@router.post("", status_code=201)
async def record_money(payload: MoneyCreate):
    if payload.date > date.today():
        raise HTTPException(422, "Record actual transactions on today or a past date.")
    if payload.workflow_id and get_workflow_service().get(payload.workflow_id) is None:
        raise HTTPException(404, "Workflow not found")
    if payload.worker_id and get_worker_service().get_worker(payload.worker_id) is None:
        raise HTTPException(404, "Employee not found")
    item = {
        **payload.model_dump(mode="json"),
        "id": uuid4().hex,
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    get_json_store().put("money", item["id"], item)
    return ApiResponse(data=item, message="Transaction recorded; no payment was sent")
