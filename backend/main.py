from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import ExtractRequest, ExtractResponse
from extractor import extract_graph

app = FastAPI(title="Text Graph MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "backend is running"}


@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest):
    return extract_graph(request.text)
