import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

from fastapi import APIRouter, HTTPException

from code.models.mt_usage import (
    Call,
    CallIn
)

from motor.motor_asyncio import AsyncIOMotorClient
from code.serializer import convert_doc, convert_doc_list

client = AsyncIOMotorClient(mongo_uri)
database = client.get_database("testdb")
collection = database.get_collection("testcol")

router = APIRouter()
call_table = {}


def find_call(call_id: int):
    return call_table.get(call_id)


@router.get("/")
async def root():
    collections = await client.list_database_names()
    return {
        "message": "Connected bla",
        "collections": collections,
    }

@router.post("/calls")
async def create_call_record(call: CallIn):
    await collection.insert_one(call.model_dump())
    return {"message": "Record created", "call": call}


@router.get("/calls", response_model=list[Call])
async def read_call_records():
    calls = await collection.find().to_list(length=10)
    return convert_doc_list(calls)


# @router.post("/calls", response_model=Call, status_code=201)
# async def create_call_record(call: CallIn):
#     data = call.dict()
#     last_record_id = len(call_table)
#     new_call = {**data, "id": last_record_id}
#     call_table[last_record_id] = new_call
#     return new_call


# @router.get("/calls", response_model=list[Call])
# async def get_all_call_records():
#     return list(call_table.values())


# @router.call("/comment", response_model=Comment, status_code=201)
# async def create_comment(comment: CommentIn):
#     call = find_call(comment.call_id)
#     if not call:
#         raise HTTPException(status_code=404, detail="call not found")

#     data = comment.dict()
#     last_record_id = len(comment_table)
#     new_comment = {**data, "id": last_record_id}
#     comment_table[last_record_id] = new_comment
#     return new_comment


# @router.get("/call/{call_id}/comment", response_model=list[Comment])
# async def get_comments_on_call(call_id: int):
#     return [
#         comment for comment in comment_table.values() if comment["call_id"] == call_id
#     ]


# @router.get("/call/{call_id}", response_model=CallWithComments)
# async def get_call_with_comments(call_id: int):
#     call = find_call(call_id)
#     if not call:
#         raise HTTPException(status_code=404, detail="call not found")

#     return {
#         "call": call,
#         "comments": await get_comments_on_call(call_id),
#     }
