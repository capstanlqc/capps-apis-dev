from enum import Enum
import json
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, Header, status, HTTPException, Depends
from code.models.mt_usage import (
    Call,
    CallIn,
    AccumulatedUsageResponse, StatOptionsResponse
)
from motor.motor_asyncio import AsyncIOMotorClient
from code.serializer import convert_doc, convert_doc_list

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
AUTH_KEY = os.getenv("AUTH_KEY")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(mongo_uri)
database = client.get_database(DB_NAME)
collection = database.get_collection("mt_usage")

router = APIRouter()


@router.post("/calls")
async def create_call_record(
        call: CallIn,
        authorization: str = Header(None) # extracts authorization header
):
    if not authorization or authorization != f"Bearer {AUTH_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # await collection.insert_one(call.model_dump())
    new_doc = await collection.insert_one(call.model_dump())
    obj_id = new_doc.inserted_id
    # doc = await collection.find_one({"_id": obj_id})
    # todo? return `"call": convert_doc(doc)` instead of `"oid": str(obj_id), "call": call` ?
    return {"message": "Record created", "oid": str(obj_id), "call": call}


@router.get("/calls", response_model=List[Call])
async def read_call_records(
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        reverse: Optional[bool] = None,
        authorization: str = Header(None)  # extracts authorization header
):
    if not authorization or authorization != f"Bearer {AUTH_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    if reverse:
        calls = await collection.find().sort("_id", -1).skip(offset).to_list(length=limit)
    else:
        calls = await collection.find().skip(offset).to_list(length=limit)
    return convert_doc_list(calls)


@router.get("/apps", response_model=List)
async def get_applications(
        authorization: str = Header(None)  # extracts authorization header
):
    data = await read_call_records(authorization=f"Bearer {AUTH_KEY}")
    apps = list(set(call["application"] for call in data))
    return sorted(apps)


@router.get("/accounts", response_model=List)
async def get_analytic_accounts(
        authorization: str = Header(None)  # extracts authorization header
):
    data = await read_call_records(authorization=f"Bearer {AUTH_KEY}")
    accounts = list(set(call["analytic_account"] for call in data))
    # AnalyticAccounts = Enum("AnalyticAccounts", accounts)
    # print(list(AnalyticAccounts))
    return sorted(accounts)

@router.get("/providers", response_model=List)
async def get_providers(
        authorization: str = Header(None)  # extracts authorization header
):
    data = await read_call_records(authorization=f"Bearer {AUTH_KEY}")
    providers = list(set(call["mt_provider"] for call in data))
    return sorted(set(p.lower() for p in providers))



@router.get("/calls/{id}", response_model=Call)
async def find_call_records_by_id(
        id: str,
        authorization: str = Header(None) # extracts authorization header
):
    if not authorization or authorization != f"Bearer {AUTH_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    call = await collection.find_one({"_id": ObjectId(id)})
    return convert_doc(call)


@router.get("/stat_options", response_model=StatOptionsResponse)
async def get_stat_options(start_date: str = '', end_date: str = ''):
    # Get filters, but only the date ones, we don't need the others
    # filters = get_filters(start_date, end_date)
    # Get unique (distinct) values
    result = {}
    for field in ['analytic_account', 'application', 'mt_provider']:
        unique_values = await collection.distinct(field) # filters[0])
        result[field] = sorted(list(set([x.lower() for x in unique_values])))
    return result


def get_filters(start_date: str = '', end_date: str = '', **kwargs) -> List[Dict]:
    """
    Helper function to conduct the matches stage of a pipeline
    """

    def filter_helper(field_name: str, field_value: str) -> Dict:
        """
        Helper function to make a case-insensitive search in MongoDB
        """
        return {"$expr": {
            "$eq": [
                {"$toLower": "$" + field_name},
                field_value.lower()
            ]
        }}

    matches = []
    today = datetime.today()
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else today.replace(day=1)
        end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else today
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    matches.append({"created_at": {"$gte": start_date, "$lte": end_date}})

    for name, value in kwargs.items():
        if value and value.lower() != "all":
            matches.append(filter_helper(name, value))

    return matches


@router.get("/stats", response_model=list[AccumulatedUsageResponse])
async def get_aggregated_data(start_date: str = '', end_date: str = '', mt_provider: str = '',
                              analytic_account: str = '', application: str = '', group_by: str = "mt_provider"):
    """
    Reads accumulated statistics based on the given parameters.
    :param str mt_provider: Filter for the MT provider
    :param str analytic_account: Filter for analytic account (project)
    :param str application: Filter for application
    :param str end_date: End date for the queried period in the YYYY-MM-DD format
    :param str start_date: Start date for the queried period in the YYYY-MM-DD format
    :param group_by: Field to use for grouping. Possible values are "date", "mt_provider" (the default), "analytic_account" and "application"
    :return: List of statistics lines
    """

    matches = get_filters(start_date, end_date, mt_provider=mt_provider, analytic_account=analytic_account, application=application)

    if group_by != 'date':
        projections = {
            group_by: {"$toLower": "$" + group_by},
            "char_count": "$char_count"
        }
        grouping = {
            "_id": "$" + group_by,
            "total_chars": {"$sum": "$char_count"}
        }
        sort_field = {group_by: 1}
    else:
        projections = {
            "date": {'$dateToString': {"format": '%Y-%m-%d', "date": '$created_at'}},
            "char_count": "$char_count"
        }
        grouping = {
            "_id": "$date",
            "total_chars": {"$sum": "$char_count"}
        }
        sort_field = {"date": 1}

    pipeline = [
        {"$match": {"$and": matches}},
        {"$project": projections},
        {"$group": grouping},
        {"$project": {group_by: "$_id", "total_chars": 1, "_id": 0}},
        {"$sort": sort_field}
    ]

    cursor = collection.aggregate(pipeline)
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
