from fastapi import FastAPI

# from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .energy_router import router as energy_router
from .solar_router import router as solar_router

app = FastAPI()

origins = ["localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solar_router, prefix="/api/solar", tags=["solar"])
app.include_router(energy_router, prefix="/api/energy", tags=["energy"])


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/")
def api():
    return {"message": "Hello Api!"}
