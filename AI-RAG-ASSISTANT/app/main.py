from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from app.rag_pipeline import ask_ai,stream_ai
from fastapi.responses import StreamingResponse
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class Question(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/ask")
def ask(question: Question):

    return StreamingResponse(
        stream_ai(question.question),
        media_type="text/plain"
    )