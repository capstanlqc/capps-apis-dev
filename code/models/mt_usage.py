from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CallIn(BaseModel):
    project: str
    application: str
    char_count: int
    source_lang: str
    target_lang: str
    # task: Literal["MT", "QE"]
    mt_provider: str
    analytic_account: Optional[str] = None
    job_id: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.today)
    # user: str

# Python’s datetime object is automatically converted to the correct BSON Date format when saved to MongoDB.
# In other words, MongoDB will store datetime.today() as a BSON Date type, which is internally represented
# as a 64-bit integer (milliseconds since the Unix epoch), which MongoDB will identify as a timestamp
# (a BSON Date type), e.g. ISODate("2025-03-27T12:00:00Z")

# However, not that the datetime object will be stored with the time zone set to UTC
# unless you explicitly specify the time zone in the datetime object.


class Call(CallIn):
    oid: str


class AccumulatedUsageResponse(BaseModel):
    total_chars: int
    application: Optional[str] = None
    date: Optional[str] = None
    analytic_account: Optional[str] = None
    mt_provider: Optional[str] = None


class StatOptionsResponse(BaseModel):
    analytic_account: list[str]
    application: list[str]
    mt_provider: list[str]
