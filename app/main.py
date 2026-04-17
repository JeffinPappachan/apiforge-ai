from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app.scraper import scrape_documentation, ScraperError
from app.llm import LLMService
from app.parser import normalize_api_structure, ParserError
from app.generator import generate_sdk


app = FastAPI(
    title="APIForge AI",
    description="Smart DevTool for API Integration",
    version="0.1.0",
)


llm_service = LLMService()


# -----------------------
# REQUEST MODELS
# -----------------------

class URLRequest(BaseModel):
    url: HttpUrl


class APIInput(BaseModel):
    base_url: str
    auth: str
    endpoints: list


# -----------------------
# ROUTES
# -----------------------

@app.get("/")
def health():
    return {"status": "ok", "service": "APIForge AI"}


@app.post("/process")
def process_api_docs(payload: URLRequest):
    try:
        # Step 1: scrape
        content = scrape_documentation(str(payload.url))

        # Step 2: LLM extraction
        raw_output = llm_service.extract_api_structure(content)

        # Step 3: parse
        structured = normalize_api_structure(raw_output)

        return {
            "api": structured,
            "summary": "API successfully analyzed."
        }

    except ScraperError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ParserError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")


@app.post("/generate")
def generate_api_sdk(payload: APIInput):
    try:
        sdk_code = generate_sdk(payload.model_dump())

        return {
            "sdk_code": sdk_code
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {e}")