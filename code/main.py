from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from code.routers.mt_usage import router as mt_usage_router


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://capps.capstan.be", "https://test.dev.nexver.hu"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# app.include_router(post_router, prefix="/api/posts")
app.include_router(mt_usage_router, prefix="/api/mt/usage")

