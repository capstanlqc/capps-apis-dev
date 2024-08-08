from pydantic import BaseModel


class CallIn(BaseModel):
    project: str
    application: str
    char_count: int
    source_lang: str
    target_lang: str
    mt_provider: str


class Call(CallIn):
    oid: str