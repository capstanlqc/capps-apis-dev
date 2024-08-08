from fastapi import FastAPI

# from code.routers.post import router as post_router
from code.routers.mt_usage import router as mt_usage_router
from code.serializer import convert_doc, convert_doc_list


app = FastAPI(
    title="cApps API",              # Custom title
    description="This is cApps API documentation.",  # Custom description
    version="1.0.0",                   # API version
    contact={
        "name": "Manuel Souto Pico",
        "url": "https://www.capstan.be",
        "email": "manuel.souto@capstan.be",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# app.include_router(post_router, prefix="/api/posts")
app.include_router(mt_usage_router, prefix="/api/mt/usage")

