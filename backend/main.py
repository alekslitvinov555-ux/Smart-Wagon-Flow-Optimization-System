from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from backend.algorithm import optimize_route as run_optimization


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
def optimize(payload: OptimizeRequest):
    result = run_optimization(payload.from_, payload.to)
    if not result["old_route"] or not result["new_route"]:
        raise HTTPException(status_code=404, detail="No route found")
    return result
