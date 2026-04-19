from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

from search import gather_research
from report import generate_report


app = FastAPI(
    title="AI Research Agent API",
    description="Generates structured market research report using Gemini + Tavily",
    version="1.0.0",
)

# CORS
# In production, this will vercel frontend URL.
# In development, it allows localhost on common ports.

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:4173",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SCHEMAS


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    topic: str
    generated_at: str
    sources_count: int
    report: dict
    charts: dict


# API ENDPOINTS


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Research Agent API",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    if len(topic) > 200:
        raise HTTPException(
            status_code=400, detail="Topic is too long. Max 200 characters."
        )

    # Phase 1: Gather research data
    try:
        research_data = gather_research(topic)

        if not research_data:
            raise HTTPException(
                status_code=503,
                detail="No research data found for the given topic. Try again!",
            )

        # Phase 2: Generate report with Gemini
        result = generate_report(topic, research_data)

        return ResearchResponse(
            topic=topic,
            generated_at=datetime.now(timezone.utc).isoformat(),
            sources_count=len(research_data),
            report=result["report"],
            charts=result["charts"],
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
