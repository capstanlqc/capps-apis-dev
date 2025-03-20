from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CallIn(BaseModel):
    project: str
    application: str
    char_count: int
    source_lang: str
    target_lang: str
    mt_provider: str
    analytic_account: Optional[str] = None
    created_at: Optional[datetime] = datetime.today()


class Call(CallIn):
    oid: str


class AccumulatedUsageRequest(BaseModel):
    start_date: str  # Format: YYYY-MM-DD
    end_date: str  # Format: YYYY-MM-DD
    application: Optional[str] = None
    analytic_account: Optional[str] = None
    mt_provider: Optional[str] = None


class AccumulatedUsageResponse(BaseModel):
    total_chars: int
    application: Optional[str] = None
    analytic_account: Optional[str] = None
    mt_provider: Optional[str] = None
