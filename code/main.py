from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from code.routers.mt_usage import router as mt_usage_router

version = "v1"
app = FastAPI(
    title="cApps ~ Toledo [track]",
    description="MT usage tracker API documentation.",
    version="1.0.0",
    openapi_url=f"/{version}/openapi.json",
    docs_url=f"/{version}/docs",
    redoc_url=f"/{version}/redoc",
    contact={
        "name": "cApStAn",
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


@app.get(f"/{version}/healthcheck", status_code=204)
async def health() -> Response:
    return Response(status_code=204)


app.include_router(mt_usage_router, prefix=f"/{version}/mt/usage")
