from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from backend.algorithm import get_mock_optimization


class OptimizeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_: str = Field(alias="from")
    to: str


app = FastAPI(title="Smart Wagon Flow Optimization System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/optimize")
def optimize_route(payload: OptimizeRequest):
    return get_mock_optimization(payload.from_, payload.to)
