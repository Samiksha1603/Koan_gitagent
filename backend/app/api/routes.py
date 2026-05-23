from fastapi import APIRouter
from pydantic import BaseModel
from app.services.pipeline import run_pipeline
from app.query.ask import ask_question

router = APIRouter()


class GenerateRequest(BaseModel):
    repo_url: str
    description: str


class AskRequest(BaseModel):
    question: str
    agent_path: str


@router.post("/generate")
def generate(request: GenerateRequest):
    return run_pipeline(
        request.repo_url,
        request.description,
    )


@router.post("/ask")
def ask(request: AskRequest):
    return ask_question(
        request.question,
        request.agent_path,
    )