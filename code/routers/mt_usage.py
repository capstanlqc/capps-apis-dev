import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from code.models.mt_usage import (
    Call,
    CallIn,
    AccumulatedUsageRequest,
    AccumulatedUsageResponse
)
from motor.motor_asyncio import AsyncIOMotorClient
from code.serializer import convert_doc, convert_doc_list

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(mongo_uri)
database = client.get_database("cappisdb")
collection = database.get_collection("mt_usage")

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
    calls = await collection.find().sort({'created_at': -1}).to_list(length=10)
    return convert_doc_list(calls)


@router.post("/stats", response_model=list[AccumulatedUsageResponse])
async def get_aggregated_data(request: AccumulatedUsageRequest, group_by: str = "mt_provider"):
    """
    Reads accumulated statistics based on the given parameters.
    Test with:
    {
      "start_date": "2025-01-01",
      "end_date": "2026-01-01",
      "application": null,
      "mt_provider": null
    }
    :param request: AccumulatedUsageRequest
    :param group_by: Field to use for grouping. Defaults to mt_provider
    :return: List of statistics lines
    """

    matches = dict()
    today = datetime.today()
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d") if request.start_date else today.replace(day=1)
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d") if request.end_date else today
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    matches["created_at"] = {"$gte": start_date, "$lte": end_date}

    if request.application and request.application != "all":
        matches["application"] = request.application

    if request.analytic_account and request.analytic_account != "all":
        matches["analytic_account"] = request.analytic_account

    if request.mt_provider and request.mt_provider != "all":
        matches["mt_provider"] = request.mt_provider

    grouping = {
        "_id": "$" + group_by, "total_chars": {"$sum": "$char_count"}
    }
    cursor = collection.aggregate([
        {"$match": matches},
        {"$group": grouping},
        {"$project": {group_by: "$_id", "total_chars": 1, "_id": 0}}
    ])
    results = list(await cursor.to_list())
    return results

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
